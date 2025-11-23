# NebuloHub

### NebuloHub = O hub onde novas ideias nascem

Nebulo vem de “Nebulosa” — estruturas cósmicas que simbolizam nascimento, criação e potencial explosivo.
É uma metáfora perfeita para startups, que também nascem pequenas e podem se tornar gigantes.

Hub representa conexão, comunidade e ponto central de encontro.

NebuloHub é uma plataforma inteligente dedicada à descoberta, avaliação e conexão de startups.
Ao se cadastrar, cada startup seleciona suas habilidades e características principais, formando um perfil único dentro do ecossistema.

Com base em avaliações públicas e no desempenho de startups semelhantes, o NebuloHub utiliza Inteligência Artificial para estimar o potencial de sucesso de cada negócio. Usuários comuns podem criar contas, acessar um feed interativo, visualizar startups, deixar avaliações em estrelas e registrar comentários, contribuindo para a formação de uma comunidade ativa e colaborativa.

Assim como estrelas surgem dentro de nebulosas, o NebuloHub funciona como um ambiente onde novas ideias ganham forma, visibilidade e direção — guiadas por dados, tecnologia e avaliação coletiva.

---

Este projeto é a solução desenvolvida para o Global Solution de "Devops" da FIAP. usando .NET 

**Integrantes:**
* Vicenzo Massao - 554833 - 2TDSPM
* Erick Alves - 556862 - 2TDSPM
* Luiz Heimberg - 556864 - 2TDSPX

**Link do Repositório GitHub:**
[Github](https://github.com/NebuloHub/IoT)

**Link do Vídeo da Apresentação:**
[Link do Video](https://youtu.be/lu7MNnmBZUU)


---

# 📘 Ferramenta de Análise de Startups e Habilidades

Este projeto é um **CLI em Python** que consome uma API para listar startups, habilidades, calcular rankings, agrupar avaliações e estimar a probabilidade de sucesso de um novo negócio baseado nas habilidades selecionadas.  
Opcionalmente, integra com o **Google Gemini** para gerar explicações automáticas.

---

# ⭐ Funcionalidades

### 🔹 Listar habilidades  
Consulta a API e lista todas as habilidades paginadas.

### 🔹 Avaliar startups  
Mostra as startups ordenadas pela média das avaliações.

### 🔹 Agrupar avaliações  
Agrupa e mostra o número de avaliações e a média por startup.

### 🔹 Cadastrar startup  
Envia um POST com os dados da startup para inclusão no sistema.

### 🔹 Calcular taxa de sucesso (IA / Gemini)  
Usa algoritmos estatísticos + pesos definidos para estimar a probabilidade de sucesso.  
Caso o Gemini esteja configurado, gera uma explicação automática.

---

# ⚙️ Pré-requisitos

- Python **3.9+**
- `pip`
- API funcionando
- Arquivo `.env` configurado

---

# 📘 Ferramenta CLI de Análise de Startups e Habilidades

Este projeto é um **CLI em Python** que consome uma API para:

- Listar habilidades  
- Rankear startups por nota média  
- Agrupar avaliações  
- Cadastrar novas startups  
- Calcular probabilidade de sucesso de um novo negócio baseado em habilidades  
- (Opcional) Integrar com o **Google Gemini** para gerar explicações

---

## 🧩 Tecnologias utilizadas

- Python 3.10+
- requests
- python-dotenv
- google-genai (opcional)

---

## 🛠️ Instalação

1. Clone o repositório ou copie o código.
2. Crie um arquivo **.env** na raiz com:

API_BASE="https://sua-api.com"
GEMINI_API_KEY="SUA_CHAVE_OPCIONAL"

3. Instale as dependências:

```bash
pip install -r requirements.txt
