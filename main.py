import os, requests
from dotenv import load_dotenv
from statistics import mean

# Configs
load_dotenv()

API_BASE = os.getenv("API_BASE")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
STARTUP_URL = f"{API_BASE}/api/v2/Startup"
HABILIDADE_URL = f"{API_BASE}/api/v2/Habilidade"

# Pesos para combinar os 3 fatores (ajuste se quiser)
WEIGHT_A = 0.6  # média das notas
WEIGHT_B = 0.25 # popularidade das habilidades
WEIGHT_C = 0.15 # correspondência das habilidades

# ===== utilidades =====
def safe_get_json(url, params=None, timeout=6):
    try:
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        # retorna None em caso de erro
        return None

def calcular_media_notas(avaliacoes):
    if not avaliacoes:
        return 0.0
    notas = [a.get("nota", 0) for a in avaliacoes if isinstance(a.get("nota", None), (int, float))]
    return mean(notas) if notas else 0.0

# ===== funcionalidades principais =====

def listar_habilidades(page_size=10):
    page = 1
    todas = []
    while True:
        data = safe_get_json(HABILIDADE_URL, params={"page": page, "pageSize": page_size})
        if not data:
            print("Erro ao buscar habilidades (ou nenhuma habilidade encontrada).")
            break
        items = data.get("items", [])
        todas.extend(items)
        total_items = data.get("totalItems", None)
        # se não houver mais items ou já recebeu menos que pageSize, para
        if len(items) < page_size:
            break
        page += 1
    # print resumido
    print("\n=== HABILIDADES ===")
    for h in todas:
        print(f"{h.get('idHabilidade')}. {h.get('nomeHabilidade')} ({h.get('tipoHabilidade')})")
    print(f"\nTotal listadas: {len(todas)}\n")
    return todas

def listar_startups(limit):
    data = safe_get_json(STARTUP_URL)
    if not data:
        print("Erro ao acessar endpoint de startups.")
        return []
    items = data.get("items", [])[:limit]
    resultados = []
    for item in items:
        self_path = item.get("links", {}).get("self")
        if not self_path:
            continue
        self_url = f"{API_BASE}{self_path}"
        detalhes = safe_get_json(self_url)
        if detalhes:
            resultados.append(detalhes)
    return resultados

def rankear_startups(limit):
    startups = listar_startups(limit)
    lista = []
    for s in startups:
        nota = calcular_media_notas(s.get("avaliacoes", []))
        habilidades = [h.get("nomeHabilidade") for h in s.get("habilidades", [])]
        lista.append({"nome": s.get("nomeStartup"), "nota": nota, "habilidades": habilidades})
    ordenadas = sorted(lista, key=lambda x: x["nota"], reverse=True)
    print("\n=== RANKING ===\n")
    for i, s in enumerate(ordenadas, start=1):
        print(f"{i}. {s['nome']} — Nota: {round(s['nota'],2)}")
        print(f"   Habilidades: {', '.join(s['habilidades']) if s['habilidades'] else 'Nenhuma'}\n")

def agrupar_avaliacoes(limit):
    startups = listar_startups(limit)
    print("\n=== AVALIAÇÕES AGRUPADAS POR STARTUP ===\n")
    for s in startups:
        nome = s.get("nomeStartup")
        avals = s.get("avaliacoes", [])
        notas = [a.get("nota") for a in avals if isinstance(a.get("nota", None), (int, float))]
        print(f"{nome} — {len(avals)} avaliações — média: {round(mean(notas),2) if notas else 'N/A'}")
    print()

def cadastrar_startup():
    print("\n=== CADASTRAR STARTUP ===")
    body = {}
    body["cnpj"] = input("CNPJ: ").strip()
    body["video"] = input("Video (URL): ").strip()
    body["nomeStartup"] = input("Nome da startup: ").strip()
    body["site"] = input("Site: ").strip()
    body["descricao"] = input("Descrição: ").strip()
    body["nomeResponsavel"] = input("Nome do responsável: ").strip()
    body["emailStartup"] = input("Email da startup: ").strip()
    body["usuarioCPF"] = input("Usuario CPF: ").strip()

    try:
        r = requests.post(STARTUP_URL, json=body, timeout=8)
        r.raise_for_status()
        print("Startup cadastrada com sucesso!")
        print("Resposta:", r.json())
    except Exception as e:
        print("Erro ao cadastrar startup:", e)

# ===== cálculo da taxa de sucesso =====

def calcular_taxa_sucesso_por_habilidades(skill_ids):
    """
    skill_ids: lista de inteiros (ids de habilidade)
    retorna: dict com métricas, taxa (0..100)
    """
    # 1) pegar todas as startups (vamos usar até 500 pra performance)
    data = safe_get_json(STARTUP_URL)
    if not data:
        return None
    items = data.get("items", [])
    # pega detalhes (self) de cada startup
    startups = []
    for item in items:
        self_path = item.get("links", {}).get("self")
        if not self_path:
            continue
        detalhes = safe_get_json(f"{API_BASE}{self_path}")
        if detalhes:
            startups.append(detalhes)

    if not startups:
        return None

    # startups que têm pelo menos uma das skills solicitadas
    def has_any_skill(s):
        ids = [h.get("idHabilidade") for h in s.get("habilidades", [])]
        return any(int(x) in skill_ids for x in ids if x is not None)

    subset = [s for s in startups if has_any_skill(s)]

    # Factor A: média das notas das startups do subset (normalizar 0..1 assumindo nota de 0..10)
    notas_subset = []
    for s in subset:
        notas = [a.get("nota", 0) for a in s.get("avaliacoes", []) if isinstance(a.get("nota", None), (int, float))]
        if notas:
            notas_subset.append(mean(notas))
    media_notas = mean(notas_subset) if notas_subset else 0.0
    factor_a = max(0.0, min(1.0, media_notas / 10.0))

    # Factor B: popularidade = proporção de startups que têm essas skills
    factor_b = len(subset) / len(startups) if startups else 0.0

    # Factor C: correspondência média de quantas das skills solicitadas aparecem em startups (0..1)
    match_ratios = []
    for s in subset:
        ids = [h.get("idHabilidade") for h in s.get("habilidades", [])]
        if not ids:
            match_ratios.append(0.0)
        else:
            matches = sum(1 for sid in skill_ids if sid in ids)
            match_ratios.append(matches / len(skill_ids) if skill_ids else 0.0)
    factor_c = mean(match_ratios) if match_ratios else 0.0

    # Combina com pesos
    combined = WEIGHT_A * factor_a + WEIGHT_B * factor_b + WEIGHT_C * factor_c
    taxa_percent = round(combined * 100, 2)

    return {
        "factor_a_media_notas": media_notas,
        "factor_a": factor_a,
        "factor_b": factor_b,
        "factor_c": factor_c,
        "taxa_percent": taxa_percent,
        "num_startups_total": len(startups),
        "num_startups_matching": len(subset)
    }

# ===== Gemini integration (opcional) =====

def chamar_gemini_explicacao(skill_ids, metrics, api_key=None):
    """
    Tenta chamar o Gemini para gerar uma explicação legível.
    Se não conseguir, retorna uma explicação local.
    """
    prompt = (
        f"Você é um assistente que avalia a probabilidade de sucesso de uma nova startup. "
        f"O usuário escolheu as habilidades (IDs): {skill_ids}.\n\n"
        f"Dados calculados:\n"
        f"- Média das notas (entre 0 e 10) das startups com essas habilidades: {metrics['factor_a_media_notas']}\n"
        f"- Proporção de startups que possuem essas habilidades: {metrics['factor_b']:.2f}\n"
        f"- Correspondência média das habilidades solicitadas: {metrics['factor_c']:.2f}\n\n"
        f"Taxa final sugerida: {metrics['taxa_percent']}%.\n\n"
        "Escreva uma explicação curta (3-5 frases) em português explicando o que essas métricas significam e recomendações práticas para aumentar a chance de sucesso."
    )

    # tenta usar google genai se disponível e chave passada
    if api_key:
        try:
            from google import genai
            # configure - dependendo da versão do client, você pode ter que setar a variável de ambiente em vez disso
            os.environ.setdefault("GOOGLE_API_KEY", api_key)
            # tentativa genérica (pode variar conforme versão da lib)
            response = genai.Text.generate(model="text-bison-001", input=prompt)
            # extrai texto - adaptamos conforme retorno possível
            text = response.output[0].content[0].text if hasattr(response, "output") else str(response)
            return text
        except Exception as e:
            # falhou ao chamar Gemini: retorna fallback
            pass

    # fallback local
    texto = (
        f"Com base nas notas médias ({round(metrics['factor_a_media_notas'],2)}/10), "
        f"na presença dessas habilidades em {metrics['num_startups_matching']} de {metrics['num_startups_total']} startups "
        f"e na correspondência média das habilidades, estimamos uma taxa de sucesso de {metrics['taxa_percent']}%.\n"
        "Para melhorar a chance: busque validar o produto com clientes rapidamente, priorize as habilidades mais presentes em startups de maior nota, "
        "e considere complementar com habilidades faltantes que aparecem com frequência em startups bem avaliadas."
    )
    return texto

# ===== menu principal =====

def avaliar_com_gemini_fluxo():
    print("\n=== AVALIAÇÃO COM GEMINI ===")
    ids_raw = input("Digite os IDs das habilidades separados por vírgula (ex: 1,2,3): ").strip()
    try:
        skill_ids = [int(x.strip()) for x in ids_raw.split(",") if x.strip()]
    except:
        print("IDs inválidos.")
        return
    metrics = calcular_taxa_sucesso_por_habilidades(skill_ids)
    if not metrics:
        print("Não foi possível calcular métricas (erro ao acessar API ou sem startups).")
        return
    print(f"\nTaxa calculada: {metrics['taxa_percent']}%")
    # tenta chamar gemini se variável de ambiente GEMINI_API_KEY estiver definida
    gemini_key = os.getenv("GEMINI_API_KEY", None)
    explicacao = chamar_gemini_explicacao(skill_ids, metrics, api_key=gemini_key)
    print("\n=== EXPLICAÇÃO ===")
    print(explicacao)
    print()

def menu():
    while True:
        print("\n=== MENU PRINCIPAL ===")
        print("1 - Avaliar startups (escolher quantidade)")
        print("2 - Listar todas as habilidades")
        print("3 - Agrupar avaliações das startups")
        print("4 - Cadastrar nova startup")
        print("5 - Avaliar (novo negócio) com Gemini (informe IDs das habilidades)")
        print("0 - Sair")
        opc = input("Escolha: ").strip()
        if opc == "1":
            print("\nQuantidades disponíveis: 5,10,15,20,30,40,50")
            q = input("Quantas startups deseja avaliar? ").strip()
            try:
                qn = int(q)
                if qn <= 0 or qn > 500:
                    print("Escolha um número entre 1 e 500.")
                else:
                    rankear_startups(qn)
            except:
                print("Valor inválido.")
        elif opc == "2":
            page_size = input("PageSize para requisições (default 10): ").strip() or "10"
            try:
                ps = int(page_size)
            except:
                ps = 10
            listar_habilidades(ps)
        elif opc == "3":
            q = input("Quantas startups considerar para agrupar avaliações? (ex: 20): ").strip() or "20"
            try:
                qn = int(q)
                agrupar_avaliacoes(qn)
            except:
                print("Valor inválido.")
        elif opc == "4":
            cadastrar_startup()
        elif opc == "5":
            avaliar_com_gemini_fluxo()
        elif opc == "0":
            print("Saindo...")
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    menu()
