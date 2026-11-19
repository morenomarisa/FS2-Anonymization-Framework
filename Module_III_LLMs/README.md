<h1 align="center">Anonimização de Dados com LLMs</h1> 
<p align="center"><i>Repositório destinado à execução de experimentos, extração de entidades sensíveis e cálculo de métricas de avaliação para anonimização de dados com LLMs.</i></p>

---

## 📋 Pré-requisitos
* **Python 3.14+**
* **PostgreSQL** (com a base de relatos e colunas rotuladas)
* **Ollama** em execução com os modelos desejados instalados, por exemplo:
  * `gemma3:1b`, `gemma3:4b`, `qwen3:4b`, etc. 

---

## 🚀 Instalação e Configuração

### 1. Clone o Repositório
```bash
git clone https://github.com/nathil/anonimizacao-de-dados-com-llms.git
cd anonimizacao-de-dados-com-llms
```

### 2. Crie e Ative o Ambiente Virtual (`.venv`)
```bash
python3 -m venv .venv
```

**Linux / macOS:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate.bat
```

### 3. Instale as Dependências
```bash
pip install -r requirements.txt
```

### 4. Configure o Arquivo `.env`
Copie o arquivo `.env.example` para `.env` e preencha com os dados do seu ambiente e do seu banco de dados:
```bash
cp .env.example .env
```

Exemplo de configuração no `.env`:
```ini
# Postgres Database Settings
POSTGRES_HOST='localhost'
POSTGRES_PORT=5432
POSTGRES_DBNAME='<your-database-name>'
POSTGRES_USER='<your-user-name>'
POSTGRES_PASSWORD='<your-password>'

# Ollama Client Settings
OLLAMA_BASE_URL='http://127.0.0.1:11434'

# Prompt Load Settings
PROMPT_FOLDER='src/prompts/'

# Outputs Folder
OUTPUT_FOLDER='outputs'

# Dataset Settings
NAME_DATABASE='<your-table-name>'
KEY_COLUMN='<your-key-column>'
REPORT_COLUMN='<your-report-column>'
NAME_COLUMN='<your-names-column>'
# CPF_CNPJ_COLUMN='<your-cpf-cnpj-column>'
# RG_COLUMN='<your-rg-column>'
# TELEPHONES_COLUMN='<your-telephones-column>'
# EMAILS_COLUMN='<your-emails-column>'
# BANK_INFORMATION_COLUMN='<your-bank-information-column>'
# ADDRESS_COLUMN='<your-address-column>'
```
> **Nota:** Caso uma coluna de entidade esteja comentada ou com valor `None` no `.env`, o sistema exibirá um erro caso você tente buscar ou calcular métricas para aquela entidade específica.

---

## 🖥️ Como Executar o Projeto

O ponto de entrada principal é o arquivo `src/main.py`, que conta com menus interativos no terminal (via **InquirerPy**):

```bash
python src/main.py
```

### Atalhos de Navegação nos Menus:
* **Setas (`↑` / `↓`)**: navegar entre as opções.
* **`Espaço`**: marcar ou desmarcar opções em listas de múltipla escolha (modelos, prompts, entidades).
* **`Ctrl + R`**: marcar/desmarcar todas as opções de uma vez (ou selecione a primeira opção `* (Select all)`).
* **`Enter`**: confirmar a seleção.

Ao iniciar `python src/main.py`, você verá o menu principal:
1. **Run tests** (Rodar testes nos LLMs)
2. **Calculate metrics** (Calcular métricas por intervalo e métricas totais)
3. **Generate charts** (Gerar gráficos e análise exploratória da base)
4. **Generate confusion matrices** (Gerar matrizes de confusão)
5. **Exit** (Sair)

---

## 🛠️ Guia das Principais Operações

### 1. Rodar Testes (`1. Run tests`)
Executa os prompts nos LLMs via Ollama para extrair entidades dos relatos.
1. Selecione os **modelos**, **prompts** e **entidades**.
2. Informe o **offset inicial** (ex.: `0`), a **quantidade de relatos por lote** (`ALL` ou número) e o **número de intervalos**.
* 📂 **Saída:** `outputs/tests/<modelo>/<prompt>/<entidade>/`

### 2. Calcular Métricas (`2. Calculate metrics`)
Extrai as entidades preditas (`tag` ou `json` conforme o cabeçalho do prompt) e calcula `TP`, `FP`, `FN`, `TN`, `Precision`, `Recall`, `F1` e `Accuracy`. Após selecionar modelos, prompts e entidades, escolha uma das opções:
* **Métricas dos Testes (`calculate the metrics interval of the tests`)**: processa os testes brutos de `outputs/tests/` e gera as métricas por relato em `outputs/metrics/`. *(Execute esta etapa primeiro)*.
* **Métricas Totais (`calculate the aggregated metrics for all tests in a folder`)**: consolida todos os arquivos de `outputs/metrics/` daquela configuração em um único resumo global em `outputs/all_metrics/`.
* **Resumo por Intervalo (`calculate all metrics of one interval tests`)**: soma as métricas de cada intervalo separadamente em `outputs/intervals_metrics/`.

### 3. Gerar Gráficos e Análise Exploratória (`3. Generate charts`)
Gera estatísticas e gráficos de distribuição de tokens da base de dados:
* **Opções 1, 2, 5, 6 e 7**: exportam métricas de tokens por relato/entidade (CSV/Excel em `outputs/`).
* **Opções 3, 4 e 8**: geram histogramas de distribuição e frequência de tokens (com IC 95%) em `outputs/` e `outputs/charts/`.

### 4. Gerar Matrizes de Confusão (`4. Generate confusion matrices`)
Gera as matrizes de confusão (`TN`, `FP`, `FN`, `TP`) a partir dos dados de `outputs/metrics/`:
* **Por intervalo (`metrics for each time interval`)**: gera um `.png` para cada intervalo testado.
* **Matriz Total (`total metrics for each model`)**: soma todos os intervalos do modelo/prompt/entidade, solicita o título e salva o gráfico consolidado (`*-total.png`).
* 📂 **Saída:** `outputs/confusionmatrix/<modelo>/<prompt>/<entidade>/`