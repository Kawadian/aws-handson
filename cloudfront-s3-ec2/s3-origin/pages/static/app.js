const byId = (id) => document.getElementById(id);

function nowText() {
  return new Date().toLocaleString("ja-JP");
}

function formatJson(value) {
  return JSON.stringify(value, null, 2);
}

async function fetchTextWithHeaders(path) {
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }

  return {
    body: await response.text(),
    headers: response.headers,
  };
}

async function fetchJson(path, options = {}) {
  const response = await fetch(path, {
    cache: "no-store",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || `${response.status} ${response.statusText}`);
  }

  return data;
}

async function loadCacheInfo() {
  byId("cache-button").disabled = true;

  try {
    const { body, headers } = await fetchTextWithHeaders("/pages/static/cache-demo.txt");
    byId("cache-body").textContent = body.trim() || "(空文字列)";
    byId("cache-x-cache").textContent = headers.get("x-cache") || "(CloudFront 経由でないため未取得)";
    byId("cache-age").textContent = headers.get("age") || "-";
    byId("cache-etag").textContent = headers.get("etag") || "-";
    byId("cache-last-modified").textContent = headers.get("last-modified") || "-";
    byId("cache-fetched-at").textContent = nowText();
  } catch (error) {
    byId("cache-body").textContent = `取得失敗: ${error.message}`;
  } finally {
    byId("cache-button").disabled = false;
  }
}

async function loadState() {
  byId("state-button").disabled = true;
  byId("state-status").textContent = "取得中...";

  try {
    const data = await fetchJson("/api/state");
    byId("state-output").textContent = formatJson(data);
    byId("state-status").textContent = `取得成功: ${nowText()}`;
  } catch (error) {
    byId("state-output").textContent = `取得失敗: ${error.message}`;
    byId("state-status").textContent = "取得失敗";
  } finally {
    byId("state-button").disabled = false;
  }
}

async function saveMemo() {
  const input = byId("memo-input");
  const text = input.value.trim();

  if (!text) {
    byId("memo-status").textContent = "メモを入力してください";
    return;
  }

  byId("memo-button").disabled = true;
  byId("memo-status").textContent = "保存中...";

  try {
    const data = await fetchJson("/api/memos", {
      method: "POST",
      body: JSON.stringify({ text }),
    });
    byId("memo-status").textContent = `保存成功: ${data.saved.text}`;
    input.value = "";
    await loadState();
  } catch (error) {
    byId("memo-status").textContent = `保存失敗: ${error.message}`;
  } finally {
    byId("memo-button").disabled = false;
  }
}

async function calculateOnServer() {
  const raw = byId("numbers-input").value;
  const numbers = raw
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean)
    .map((item) => Number(item));

  if (!numbers.length || numbers.some((value) => Number.isNaN(value))) {
    byId("calc-output").textContent = "数値をカンマ区切りで入力してください。例: 10, 20, 35";
    return;
  }

  byId("calculate-button").disabled = true;

  try {
    const data = await fetchJson("/api/calculate", {
      method: "POST",
      body: JSON.stringify({ numbers }),
    });
    byId("calc-output").textContent = formatJson(data);
  } catch (error) {
    byId("calc-output").textContent = `計算失敗: ${error.message}`;
  } finally {
    byId("calculate-button").disabled = false;
  }
}

window.addEventListener("DOMContentLoaded", () => {
  byId("cache-button").addEventListener("click", loadCacheInfo);
  byId("state-button").addEventListener("click", loadState);
  byId("memo-button").addEventListener("click", saveMemo);
  byId("calculate-button").addEventListener("click", calculateOnServer);
});
