# Declaração de uso de IA

Usei assistentes de IA neste desafio. Abaixo estão as ferramentas, os modelos e a divisão do trabalho.

## Ferramentas e modelos

| Ferramenta | Modelo | Uso |
|-|-|-|
| Codex (OpenAI) | GPT-6.1 Sol (app desktop do Codex) | Opiniões e revisão pontuais no início do projeto |
| Claude Code (app desktop da Anthropic, aba Code) | Claude Sonnet 5.5 (`claude-sonnet-5-5`) | Primeira leitura da pasta do projeto |
| Claude Code (app desktop da Anthropic, aba Code) | Claude Opus 5.5 (`claude-opus-5-5`) | Reprodução, correções, testes, validação, documentação e PDF |

## Sessões

- [`sessao-01.md`](sessao-01.md): log consolidado da sessão do Codex.
- [`sessao-02.md`](sessao-02.md): log consolidado da sessão do Claude Code.

## O que a IA fez

**Codex:** opinou e revisou pontualmente o início do projeto.

**Claude Code:**
- Montou o ambiente com Python 3.11 e registrou a linha de base antes de qualquer alteração (5 testes
  falhando e os relatórios originais).
- Fez o perfil dos dados, reproduziu e confirmou as 5 suspeitas e corrigiu cada uma na causa raiz.
- Acrescentou validações para que entradas inválidas saiam com o código 2, conforme o contrato.
- Escreveu os 58 testes adicionais e o script de conferência independente, e reintroduziu cada defeito
  para provar que os testes o detectam. Isso revelou e fechou uma brecha (multiplicação via `float`).
- Redigiu o `README-ENTREGA.md`, esta declaração (para minha revisão) e o relatório técnico em PDF, e
  configurou o CI.

## O que eu fiz

Assumi a liderança técnica do trabalho, da definição do escopo à entrega:

- **Direção e escopo.** Defini o objetivo e o padrão de qualidade da entrega e conduzi o trabalho em
  etapas, aprovando cada passo antes de avançar.
- **Rigor sobre as sugestões.** Tratei toda proposta das IAs como hipótese a ser comprovada, nunca como
  verdade, e questionei as escolhas antes de aceitá-las.
- **Decisões de entrega.** Defini o agrupamento do histórico de commits por assunto, a medida do destaque
  dado às ferramentas de IA na documentação e o foco da documentação de testes no que eles efetivamente
  comprovam.
- **Comunicação técnica.** Solicitei um relatório técnico em PDF para registrar o raciocínio, os
  argumentos e as decisões, indo além do código.
- **Revisão final.** Revisei as explicações e os resultados antes da publicação.

## Verificações feitas por mim

Validei o resultado por conta própria, sem depender apenas dos relatos das ferramentas:

- **Suíte de testes.** Executei `pytest -q` no meu próprio terminal e confirmei `63 passed`.
- **Amostra de validação.** Executei o CLI sobre a amostra do desafio e confrontei o resumo (12 reservas,
  9 confirmadas, 28 noites, total `7566.00`) com a tabela esperada no README.
- **Relatório técnico.** Revisei o PDF e determinei ajustes de forma e de conteúdo: texto em voz
  impessoal, remoção de uma seção de próximos passos genéricos e menor destaque ao uso do Codex.
- **Declaração e histórico.** Revisei esta declaração e o histórico de commits, e solicitei a
  consolidação de ajustes pequenos de texto no commit de documentação.
