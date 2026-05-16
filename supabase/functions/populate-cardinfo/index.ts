import { createClient } from "npm:@supabase/supabase-js@2";
import Papa from "npm:papaparse@5.4.1";

const TCGCSV_BASE_URL = "https://tcgcsv.com";
const CATEGORY_ID = 3; // EN Pokémon

const APP_NAME = "PkmonCardsTracker";
const APP_VERSION = "1.0.0";
const CONTACT_EMAIL = "your-email@example.com";
const USER_AGENT = `${APP_NAME}/${APP_VERSION} (contact: ${CONTACT_EMAIL})`;

const GROUP_CONCURRENCY = 6;
const UPSERT_BATCH_SIZE = 1000;
const FETCH_TIMEOUT_MS = 120_000;

function env(name: string): string {
  const v = Deno.env.get(name);
  if (!v) throw new Error(`Missing env var: ${name}`);
  return v;
}

function json(status: number, body: unknown) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function asInt(x: unknown): number | null {
  if (x === null || x === undefined) return null;
  const s = String(x).trim();
  if (!s) return null;
  const n = Number.parseInt(s, 10);
  return Number.isFinite(n) ? n : null;
}

function trimOrNull(x: unknown): string | null {
  if (x === null || x === undefined) return null;
  const s = String(x).trim();
  return s || null;
}

function asArrayOrNull(x: unknown): string[] | null {
  const s = trimOrNull(x);
  if (!s) return null;
  // Some TCGCSV fields are comma-separated, some are a single value.
  const parts = s.split(/\s*,\s*/).filter(Boolean);
  return parts.length ? parts : null;
}

function deriveSupertype(extCardType: string | null): string | null {
  if (!extCardType) return null;
  const t = extCardType.toLowerCase();
  if (/(item|supporter|stadium|tool|trainer)/.test(t)) return "Trainer";
  if (/energy/.test(t)) return "Energy";
  return "Pokémon";
}

function parseRetreatCost(x: unknown): string[] | null {
  const s = trimOrNull(x);
  if (!s) return null;
  const n = Number.parseInt(s, 10);
  if (Number.isFinite(n) && n >= 0) {
    return Array.from({ length: n }, () => "Colorless");
  }
  return [s];
}

async function fetchWithTimeout(url: string, timeoutMs: number) {
  const controller = new AbortController();
  const t = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, {
      signal: controller.signal,
      headers: { "User-Agent": USER_AGENT },
    });
  } finally {
    clearTimeout(t);
  }
}

async function fetchJson(path: string) {
  const url = `${TCGCSV_BASE_URL}/${path.replace(/^\//, "")}`;
  const resp = await fetchWithTimeout(url, FETCH_TIMEOUT_MS);
  if (!resp.ok) {
    throw new Error(`GET ${url} failed: ${resp.status} ${await resp.text()}`);
  }
  return await resp.json();
}

async function fetchCsv(path: string): Promise<Record<string, string>[]> {
  const url = `${TCGCSV_BASE_URL}/${path.replace(/^\//, "")}`;
  const resp = await fetchWithTimeout(url, FETCH_TIMEOUT_MS);

  if (resp.status === 404) return [];
  if (!resp.ok) {
    throw new Error(`GET ${url} failed: ${resp.status} ${await resp.text()}`);
  }

  const text = await resp.text();
  const parsed = Papa.parse<Record<string, string>>(text, {
    header: true,
    skipEmptyLines: true,
  });

  if (parsed.errors?.length) {
    console.warn("CSV parse errors:", parsed.errors.slice(0, 3));
  }
  return (parsed.data ?? []).filter(Boolean);
}

async function getGroups(): Promise<any[]> {
  const groupsData = await fetchJson(`tcgplayer/${CATEGORY_ID}/groups`);
  return groupsData?.results ?? [];
}

function extractCards(rows: Record<string, string>[]) {
  const out: any[] = [];

  for (const row of rows) {
    if (String(row["categoryId"] ?? "").trim() !== String(CATEGORY_ID)) continue;

    const productId = asInt(row["productId"]);
    if (productId === null) continue;

    // Skip sealed products - cardinfo is for actual cards only.
    const number = trimOrNull(row["extNumber"]);
    if (!number) continue;

    const cardName = trimOrNull(row["name"]);
    if (!cardName) continue;

    const extCardType = trimOrNull(row["extCardType"]);
    const supertype = deriveSupertype(extCardType);

    out.push({
      id: String(productId),
      card_name: cardName,
      number,
      hp: trimOrNull(row["extHP"]),
      supertype,
      subtypes: extCardType ? [extCardType] : null,
      pokemon_types: null,
      resistance: asArrayOrNull(row["extResistance"]),
      weakness: asArrayOrNull(row["extWeakness"]),
      retreat_cost: parseRetreatCost(row["extRetreatCost"]),
      set_id: trimOrNull(row["groupId"]),
      productid: productId,
      type: trimOrNull(row["subTypeName"]),
    });
  }

  return out;
}

function dedupeById(objs: any[]) {
  const map = new Map<string, any>();
  for (const o of objs) map.set(o.id, o);
  return Array.from(map.values());
}

async function upsertCardinfo(
  supabaseAdmin: ReturnType<typeof createClient>,
  objs: any[],
) {
  if (!objs.length) return;

  for (let i = 0; i < objs.length; i += UPSERT_BATCH_SIZE) {
    const batch = dedupeById(objs.slice(i, i + UPSERT_BATCH_SIZE));

    const { error } = await supabaseAdmin
      .from("cardinfo")
      .upsert(batch, { onConflict: "id" });

    if (error) throw new Error(`Supabase upsert error: ${error.message}`);
  }
}

async function mapPool<T, R>(
  items: T[],
  concurrency: number,
  fn: (item: T, idx: number) => Promise<R>,
): Promise<R[]> {
  const results: R[] = new Array(items.length);
  let next = 0;

  const workers = Array.from({ length: Math.max(1, concurrency) }, async () => {
    while (true) {
      const idx = next++;
      if (idx >= items.length) break;
      results[idx] = await fn(items[idx], idx);
    }
  });

  await Promise.all(workers);
  return results;
}

Deno.serve(async (_req) => {
  const startedAt = Date.now();

  try {
    const supabaseAdmin = createClient(env("SUPABASE_URL"), env("SUPABASE_SERVICE_ROLE_KEY"), {
      auth: { persistSession: false },
    });

    console.log(`cardinfo update: fetching groups for categoryId=${CATEGORY_ID}...`);
    const groups = await getGroups();
    console.log(`Found ${groups.length} groups.`);

    let totalCsvRowsRead = 0;

    const perGroup = await mapPool(groups, GROUP_CONCURRENCY, async (group: any, idx: number) => {
      const groupId = group?.groupId;
      const groupName = group?.name ?? "";
      if (!groupId) return [];

      console.log(`[${idx + 1}/${groups.length}] Group ${groupId} - ${groupName}`);

      const path = `tcgplayer/${CATEGORY_ID}/${groupId}/ProductsAndPrices.csv`;
      const csvRows = await fetchCsv(path);
      totalCsvRowsRead += csvRows.length;

      const cards = extractCards(csvRows);
      console.log(`  -> ${cards.length} cards`);
      return cards;
    });

    const allCards = perGroup.flat();
    console.log(`Total raw CSV rows read: ${totalCsvRowsRead}`);
    console.log(`Total cards collected: ${allCards.length}`);

    await upsertCardinfo(supabaseAdmin, allCards);

    return json(200, {
      ok: true,
      categoryId: CATEGORY_ID,
      groups: groups.length,
      totalCsvRowsRead,
      totalCards: allCards.length,
      tookMs: Date.now() - startedAt,
      ranAt: new Date().toISOString(),
    });
  } catch (e) {
    console.error(e);
    return json(500, {
      ok: false,
      error: String((e as any)?.message ?? e),
      tookMs: Date.now() - startedAt,
    });
  }
});
