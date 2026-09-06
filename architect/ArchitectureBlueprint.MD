# 🛠️ Skill & Architecture Blueprint: [Nome do Projeto]

Este documento descreve o padrão de engenharia, arquitetura e processos de qualidade adotados neste projeto. O objetivo é fornecer uma visão clara de como os requisitos de negócio são traduzidos em código escalável, testável e de fácil manutenção.

---

## 1. 📊 Análise e Modelagem de Negócio (Domain-Driven Design)

Todo o desenvolvimento começa pela compreensão profunda do problema. A modelagem segue os princípios do **DDD (Domain-Driven Design)** para garantir que o código reflita exatamente a linguagem e as regras do negócio.

*   **Linguagem Ubíqua:** Termos de negócio são mapeados diretamente para nomes de classes, métodos e variáveis.
*   **Bounded Contexts:** Separação clara das fronteiras de responsabilidade (ex: Contexto de Vendas, Contexto de Estoque).
*   **Agregados e Entidades:** Definição de raízes de agregação (*Aggregate Roots*) para garantir a consistência transacional das regras de negócio. Validações de estado ocorrem estritamente dentro do Domínio.

---

## 2. 🏛️ Arquitetura de Backend (Clean Architecture & CQRS)

O backend é projetado para ser independente de frameworks, bancos de dados e interfaces externas, seguindo a **Clean Architecture**.

### Estrutura Baseada em Features (Vertical Slices)
Em vez de organizar o projeto por camadas técnicas genéricas (Controllers, Services, Repositories), o código é agrupado por **Features** (ex: `Features/Orders`, `Features/Payments`). Isso aumenta a coesão e facilita a manutenção.

### Padrão CQRS (Command Query Responsibility Segregation)
A manipulação e a leitura de dados são estritamente separadas:
*   **Commands:** Classes que encapsulam a intenção de alterar o estado da aplicação (Criar, Atualizar, Deletar). Cada Command possui um *Handler* específico que orquestra a lógica e validações.
*   **Queries:** Classes responsáveis apenas por ler dados. Otimizadas para performance, frequentemente retornando DTOs (Data Transfer Objects) diretamente do banco sem passar pelo peso do tracking do ORM.

### Camadas da Aplicação
1.  **Domain:** Entidades puras, Value Objects e Domain Events. (Sem dependências externas).
2.  **Application:** Casos de uso (Features), Command/Query Handlers e interfaces.
3.  **Infrastructure:** Implementação de acesso a dados, integrações com APIs externas, envio de e-mails e serviços de infraestrutura.
4.  **Presentation / API:** Endpoints REST/GraphQL enxutos que apenas despacham (dispatch) os Commands e Queries para a camada de aplicação.

---

## 3. 💾 Banco de Dados e Implementação (CRUD Patterns)

*   **Modelagem Relacional:** Tabelas desenhadas em 3FN (Terceira Forma Normal), com índices otimizados para as Queries mais frequentes.
*   **Padrão Repository:** Utilizado para abstrair o acesso a dados dos *Aggregate Roots* durante a execução de Commands.
*   **Migrações (Migrations):** Controle de versão do banco de dados automatizado, garantindo que a evolução do schema acompanhe as entregas de código.
*   **Unit of Work:** Garantia de atomicidade nas transações. Múltiplas alterações no banco são comitadas juntas ou desfeitas em caso de erro (Rollback).

---

## 4. ⚛️ Frontend (React & Feature Pattern)

O ecossistema frontend em **React** reflete a maturidade do backend, adotando uma arquitetura modular que escala junto com o crescimento da aplicação.

*   **Arquitetura Orientada a Features:** Espelhando o backend, os componentes, hooks de estado e chamadas de API são isolados dentro de pastas por contexto (ex: `/src/features/auth`, `/src/features/dashboard`).
*   **Gestão de Estado Assíncrono:** Utilização de ferramentas modernas (como React Query, SWR ou RTK Query) para cache, sincronização em background e refetching otimizado, lidando de forma nativa com a natureza das *Queries* do backend.
*   **Componentização UI:** Componentes de apresentação (Dumb Components) isolados das regras de negócio (Smart Components), facilitando o reuso e a implementação de Design Systems.
*   **Tratamento de Comandos:** Feedback visual imediato em formulários e botões de ação enquanto os *Commands* são processados pela API, lidando de forma elegante com estados de loading e erros.

---

## 5. 🧪 Estratégia de Testes e Qualidade

A confiabilidade do sistema é garantida através de uma pirâmide de testes bem definida:

*   **Testes de Unidade (Unit Tests):** Foco implacável na camada de `Domain` e nos `Command Handlers`. Garantem que as regras de negócio e validações funcionem de forma isolada, rápida e sem dependências externas.
*   **Testes de Integração (Integration Tests):** Validação da camada de `Infrastructure`. Garantem que os Repositórios conversem corretamente com o banco de dados e que as integrações externas funcionem como o esperado.
*   **Testes de Frontend:** Testes de componentes isolados (Testing Library) focados em acessibilidade e comportamento do usuário, além de mocks de API para garantir que as requisições enviadas ao backend tenham os payloads corretos.

---

## 🚀 Como iniciar com este Padrão

1. Analise o problema de negócio e defina as Entidades e Agregados no Domínio.
2. Crie as migrações de Banco de Dados baseadas nos modelos de negócio.
3. Crie a pasta da Feature na camada de Aplicação.
4. Implemente os `Commands` e `Queries` necessários para aquela Feature.
5. Exponha os endpoints na API e conecte a interface em React consumindo a nova funcionalidade.
