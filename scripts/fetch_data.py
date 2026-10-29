import os, json, httpx, anthropic

H = {"X-Auth-Token": os.environ["FOOTBALL_API_KEY"]}
B = "https://api.football-data.org/v4/competitions/PL"

def get(p):
    r = httpx.get(B + p, headers=H, timeout=30)
    r.raise_for_status()
    return r.json()

def save(name, data):
    os.makedirs("data", exist_ok=True)
    with open(f"data/{name}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

def short(m):
    return {"home": m["homeTeam"]["name"], "away": m["awayTeam"]["name"],
            "date": m["utcDate"], "score": m["score"]["fullTime"]}

table = get("/standings")["standings"][0]["table"]
results = [short(m) for m in get("/matches?status=FINISHED")["matches"][-10:]]
fixtures = [short(m) for m in get("/matches?status=SCHEDULED")["matches"][:10]]
save("table", table)
save("results", results)
save("fixtures", fixtures)

top = [(t["position"], t["team"]["name"], t["points"]) for t in table[:10]]
prompt = (f"Tabela: {top}\nOstatnie wyniki: {results}\nNadchodzące: {fixtures[:5]}\n"
          "Po polsku, krótko: dla każdego z 5 nadchodzących meczów analiza "
          "i typ z prawdopodobieństwami 1/X/2. To rozrywka, nie porada bukmacherska.")
msg = anthropic.Anthropic().messages.create(
    model="claude-sonnet-5-5", max_tokens=1500,
    messages=[{"role": "user", "content": prompt}])
save("analysis", {"text": msg.content[0].text})
