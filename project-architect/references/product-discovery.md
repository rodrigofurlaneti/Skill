# Product Discovery & Requirements — PO Agent

Este guia estabelece os padrões para mapeamento de processos, análise de requisitos e tradução de necessidades de negócio para especificações técnicas.

## 1. Mapeamento de Processo (AS-IS / TO-BE)
- **Fluxo Principal**: Identifique o caminho feliz (Happy Path) do usuário.
- **Fluxos Alternativos**: Mapeie exceções, erros e regras de borda.
- **Atores**: Defina claramente quem interage com o sistema (Persona, Admin, API externa).

## 2. Escrita de User Stories (Padrão INVEST)
- **Estrutura**: "Como [ator], eu quero [ação], para que [valor de negócio]."
- **Critérios de Aceite**: Liste em formato Gherkin (Dado que... Quando... Então...) para facilitar a criação de testes automáticos futuramente.

## 3. Priorização (MoSCoW)
- **Must Have**: O essencial para o MVP.
- **Should Have**: Importante, mas não vital.
- **Could Have**: Desejável se houver tempo.
- **Won't Have**: Fora do escopo atual.

## 4. Definição de Requisitos Não-Funcionais
- Segurança (Compliance), Performance (Latência), Escalabilidade (Carga) e Disponibilidade.