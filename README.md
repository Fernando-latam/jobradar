# JobRadar

Coletor de vagas com filtro de elegibilidade geográfica.

Agrega vagas de vários job boards e descarta automaticamente as que exigem
residência ou autorização de trabalho em países onde você não pode ser
contratado — o problema que faz a maior parte das candidaturas internacionais
serem perda de tempo.

---

## Por que isso existe

Boa parte das vagas anunciadas como "remote" são, na prática, restritas a um
país. Uma amostra de 9 vagas de L&D marcadas como remotas mostrou 9 fechadas
para um candidato baseado no Brasil — por autorização de trabalho, residência
exigida ou listas de países que omitiam o Brasil.

O filtro deste projeto lê a localização e a descrição de cada vaga e classifica
em três grupos:

| Status | Significado |
|---|---|
| **Elegível** | Sinal explícito de Brasil, LATAM, contratação global ou EOR |
| **Talvez** | Nada conclusivo — vale abrir e verificar |
| **Bloqueada** | Restrição explícita de país, residência ou autorização |

---

## Como rodar (sem instalar nada)

### 1. Criar a conta e o repositório

1. Crie uma conta em [github.com](https://github.com) (grátis).
2. Clique em **New repository**, dê o nome `jobradar` e marque **Public**.
   (Público é intencional: o repositório serve como portfólio.)
3. Clique em **uploading an existing file** e arraste todos os arquivos
   deste projeto, preservando as pastas.

### 2. Liberar as permissões

Em **Settings → Actions → General → Workflow permissions**, marque
**Read and write permissions** e salve. Sem isso o robô não consegue publicar
o relatório.

### 3. Rodar pela primeira vez

Na aba **Actions**, clique em **JobRadar** → **Run workflow**.
A execução leva de 2 a 5 minutos.

### 4. Ver o resultado

Depois que rodar, o relatório fica disponível de duas formas:

- **Artifact**: na página da execução, seção *Artifacts*, baixe `jobradar-report`
  e abra o `index.html`.
- **Página web** (recomendado): em **Settings → Pages**, escolha
  *Deploy from a branch* → branch `gh-pages` → `/root` → Save.
  Em poucos minutos seu relatório fica em
  `https://SEU-USUARIO.github.io/jobradar/` — abre em qualquer celular.

A partir daí ele roda sozinho todo dia às 7h de Brasília.

---

## Como ajustar

Tudo que você vai querer mudar está em **`config.py`**. Não é preciso mexer no
resto do código.

### Títulos de vaga

```python
TITLE_KEYWORDS = ["instructional design", "enablement", ...]
TITLE_EXCLUDE  = ["software engineer", "personal trainer", ...]
```

Adicione ou remova expressões. A comparação ignora maiúsculas e acentos de
capitalização, e basta uma expressão aparecer no título.

### Empresas monitoradas

O maior ganho vem de monitorar empresas específicas direto na fonte — você vê a
vaga no dia em que é publicada, antes de aparecer nos agregadores.

```python
GREENHOUSE_COMPANIES = ["deel", "gitlab", ...]
LEVER_COMPANIES      = ["netlify", ...]
ASHBY_COMPANIES      = ["linear", ...]
```

Para descobrir o identificador de uma empresa, procure a página de carreiras
dela. Se a URL for:

- `boards.greenhouse.io/**empresa**` → adicione `"empresa"` em `GREENHOUSE_COMPANIES`
- `jobs.lever.co/**empresa**` → `LEVER_COMPANIES`
- `jobs.ashbyhq.com/**empresa**` → `ASHBY_COMPANIES`

Vale conferir o diagnóstico no fim do relatório: empresas que não responderam
aparecem listadas, geralmente porque o identificador está errado ou a empresa
mudou de plataforma.

### Regras geográficas

```python
GEO_NEGATIVE     # frases que bloqueiam a vaga
GEO_COUNTRY_LOCK # países que, na localização, travam a vaga
LATAM_COUNTRIES  # se 2+ aparecem sem o Brasil, bloqueia
GEO_POSITIVE     # sinais de contratação global / EOR
```

Ajuste conforme for vendo falsos positivos e negativos no relatório. Essa
calibração é normal nas primeiras semanas.

### Horário

Em `.github/workflows/jobradar.yml`:

```yaml
- cron: '0 10 * * 1-5'   # 10h UTC = 7h Brasília, seg-sex
```

---

## Estrutura

```
config.py               ← o único arquivo que você edita
run.py                  ponto de entrada
filters.py              deduplicação, filtro de título, filtro geográfico, score
report.py               gera o HTML
collectors/sources.py   um coletor por fonte
.github/workflows/      automação diária
```

Sem dependências externas: usa apenas a biblioteca padrão do Python.

---

## Fontes

| Fonte | Tipo | Precisa de lista? |
|---|---|---|
| RemoteOK | JSON público | não |
| Remotive | JSON público | não |
| We Work Remotely | RSS | não |
| Himalayas | JSON público | não |
| Greenhouse | API por empresa | sim |
| Lever | API por empresa | sim |
| Ashby | API por empresa | sim |

Todas são interfaces públicas e documentadas. O projeto não faz scraping de
sites que proíbem acesso automatizado, e por isso não inclui LinkedIn nem
Indeed — para esses, use alertas nativos por email.

---

## Solução de problemas

**Todas as fontes falharam.** Provavelmente restrição de rede no ambiente onde
rodou. No GitHub Actions isso não costuma acontecer; rodando localmente, pode
ser firewall ou proxy corporativo.

**Muitas vagas em "Talvez".** Normal no começo. Leia algumas, veja que padrão de
texto elas têm, e acrescente as frases correspondentes a `GEO_POSITIVE` ou
`GEO_NEGATIVE`.

**Uma vaga elegível foi bloqueada.** Abra o relatório e veja o motivo indicado
no card. Se a regra estiver ampla demais, ajuste a lista correspondente em
`config.py`.

**Nenhuma vaga da minha área.** Amplie `TITLE_KEYWORDS`. Vale conferir se algum
termo em `TITLE_EXCLUDE` está removendo mais do que deveria.

---

## Roadmap

- [x] Fase 1 — coletores, filtro geográfico, relatório HTML
- [ ] Fase 2 — pontuação com LLM lendo a descrição contra o perfil, envio por email
- [ ] Fase 3 — ingestão de alertas de email, histórico de vagas já vistas
