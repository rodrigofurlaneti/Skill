# AGENTS.md — Frontend NAME_PROJECT

Guia de padrões do frontend. Leia antes de criar ou alterar qualquer código em `frontend/`.

Descreve o que o projeto **faz hoje**, não um ideal. Quando houver divergência entre este
documento e o código, o código vence — e o documento deve ser corrigido.

---

## 1. Stack

| Item | Escolha |
|---|---|
| Build | Vite 5 + `@vitejs/plugin-react` |
| Linguagem | TypeScript 5.6, `strict: true`, `noUnusedLocals`, `noUnusedParameters` |
| UI | React 18 |
| Rotas | react-router-dom 6 |
| Estado de servidor | **TanStack React Query 5** |
| Estado de cliente | **Zustand 4** com `persist` |
| Formulários | react-hook-form 7 + **Zod 3** via `@hookform/resolvers` |
| Máscaras | react-input-mask 2 |
| Notificação | `sonner` (toast) e `sweetalert2` (diálogo modal) |
| Estilo | **CSS puro com custom properties** — ver §7 |
| E2E | Playwright |
| Docs de componente | Storybook 8 |

Scripts:

```bash
npm run dev        # vite, porta 5173
npm run build      # tsc -b && vite build  ← o typecheck é o gate do CI
npm run test:e2e   # playwright
npm run storybook
```

⚠️ **Não existe script de lint.** O `eslint` está em devDependencies mas sem configuração nem
script. O que reprova no CI é o `tsc -b` do `npm run build`.

---

## 2. Estrutura

```
src/
  main.tsx        providers: ErrorBoundary > QueryClient > Toast > Dialog > BrowserRouter
  App.tsx         TODAS as rotas, em um arquivo só
  features/<área>/   uma pasta por domínio de negócio
  components/     componentes de aplicação (conhecem domínio/estado): AppShell,
                  CompanyContextGate, DataTable, MetricCard, PageHeader, QueryError...
  ui/             primitivos burros e reutilizáveis: Button, Field, Modal, Toast,
                  Dialog, StatusBadge, EmptyState, Skeleton — exportados por ui/index.ts
  lib/
    apiClient.ts  api(), apiUpload(), ApiError — ver §3
    types.ts      tipos de resposta da API compartilhados entre features
    swal.ts       wrappers do sweetalert2
  stores/         authStore, themeStore (Zustand + persist)
  styles/global.css   design system inteiro (~57 KB, arquivo único)
  utils/
test/features/<área>/   specs Playwright espelhando features/
```

**`ui/` vs `components/`:** se o componente importa store, React Query ou tipo de domínio, ele é
`components/`. Se recebe tudo por prop e serve a qualquer tela, é `ui/`.

### Anatomia de uma feature

```
features/<área>/
  <Área>Page.tsx        componente de página, ligado a uma rota em App.tsx
  api.ts                funções de chamada HTTP tipadas (ou <coisa>Api.ts)
  <Área>Schema.ts       schema Zod, quando há formulário
  hooks.ts              hooks de React Query da área
  <Painel>.tsx          subcomponentes da tela
  <Área>Page.css        CSS específico, quando não cabe no global.css
```

Nomes de pasta são minúsculos e sem separador (`diningareas`, `publicOrdering`, `storeFront` —
a inconsistência de casing já existe; siga a pasta que você for tocar).

---

## 3. Acesso à API — sempre pelo `lib/apiClient`

**Nunca chame `fetch` direto.** Use `api<T>()` ou `apiUpload<T>()`.

```ts
import { api, apiUpload, ApiError } from "../../lib/apiClient";

export const getCategories = (companyId: number): Promise<CategoryResponse[]> =>
  api<CategoryResponse[]>(`/api/categories/company/${companyId}`);

export const createCategory = (companyId: number, name: string): Promise<number> =>
  api<number>("/api/categories", {
    method: "POST",
    body: JSON.stringify({ companyId, name }),
  });
```

O que o client faz por você:

- injeta `Authorization: Bearer <accessToken>` e os headers `X-Company-Id` / `X-Branch-Id`;
- em **401**, tenta `POST /api/auth/refresh` uma vez e repete a requisição; se falhar, limpa a
  sessão e lança `ApiError(401, "Auth.SessionExpired")`;
- aborta com `ApiError(409, "Company.ContextChanged")` se a empresa/filial ativa mudou no meio da
  requisição — evita gravar dado no tenant errado;
- traduz `ProblemDetails` do backend: `ApiError.code` recebe o `title` (que é o `Error.Code` do
  backend, ex.: `"Cep.NotFound"`) e `ApiError.message` recebe o `detail`;
- devolve `undefined` em **204**;
- converte falha de rede em `ApiError(0, "Network.Unreachable")`.

Requisição sem token funciona (telas públicas: login, cadastro, storefront) — o header
`Authorization` simplesmente não é enviado.

### Tratar erro por código, não por texto

```ts
export function describeCepError(error: unknown): string {
  if (!(error instanceof ApiError)) return "Não foi possível consultar o CEP.";
  switch (error.code) {
    case "Cep.NotFound":      return "CEP não encontrado na base dos Correios.";
    case "ViaCep.RateLimited": return "Muitas consultas seguidas. Aguarde.";
    default:                   return "Consulta indisponível. Preencha manualmente.";
  }
}
```

Os códigos vêm do `Error.Code` do backend (`<Contexto>.<Motivo>`). Ver `AGENTS.md` do backend, §4.

---

## 4. React Query

Configuração global em `main.tsx`: `retry: 1`, `staleTime: 10_000`, `refetchOnWindowFocus: true`.

- **`queryKey` inclui o escopo**: `["access", "my", userName]`, `["allowed-companies", companyId]`,
  `["company-branches", companyId]`. Chave sem o `companyId` vaza cache entre empresas.
- `enabled:` para query que depende de pré-condição (`enabled: accessToken !== null`).
- `staleTime` maior para dado que quase não muda (features do usuário: `60_000`).
- Hooks de query ficam em `features/<área>/hooks.ts`.
- Erro de carregamento renderiza `<QueryError error={q.error} what="categorias" />`.
- Mutação usa `useMutation` + `toast.success` / `toast.error` do `sonner`, e invalida a query
  afetada no `onSuccess`.

---

## 5. Formulários

Padrão: react-hook-form + `zodResolver`, com `mode: "onBlur"`.

```tsx
const { register, handleSubmit, control, watch, setValue, getValues, setFocus,
        formState: { errors, isSubmitting } } = useForm<SignupFormData>({
  resolver: zodResolver(signupSchema),
  mode: "onBlur",
  defaultValues: { branchName: "Matriz" },
});
```

- O schema Zod fica em arquivo próprio (`signupSchema.ts`) e exporta o tipo:
  `export type SignupFormData = z.infer<typeof signupSchema>`.
- Campo com máscara usa `<Controller>` + `<InputMask>`.
- **Máscara:** em `react-input-mask` só `9`, `a` e `*` são coringas. `0` é **caractere
  literal** — `"99.999.999/0000-99"` não captura os dígitos da filial (bug real que já existiu
  aqui). CNPJ é `"99.999.999/9999-99"`, CPF `"999.999.999-99"`, CEP `"99999-999"`.
- Telefone brasileiro tem 10 (fixo) ou 11 (celular) dígitos — use máscara dinâmica
  (`phoneMaskFor` em `features/signup/cnpjUtils.ts`), não uma fixa de 11.
- O payload é limpo antes de enviar: `replace(/\D/g, "")` em documentos, string vazia → `undefined`
  em campo opcional (`orUndefined` em `signupApi.ts`).

### Autopreenchimento (CNPJ, CEP)

Já existe um padrão consolidado em `features/signup/`:

```
cnpjUtils.ts / cepUtils.ts   normalização, validação de dígito, formatação
cnpjApi.ts / cepApi.ts       tipos da resposta + describeXError
useCnpjAutofill.ts           hook: dispara no blur, preenche, controla estado
autofillTracker.ts           registro de procedência COMPARTILHADO
```

Regras que esse padrão respeita e que você deve manter:

1. **Valide no cliente antes de chamar** (dígito verificador), para não gastar cota de API externa.
2. **Aborte a requisição anterior** com `AbortController` e não repita o mesmo valor
   (`lastQueriedRef`).
3. **Nunca sobrescreva o que o usuário digitou.** O `autofillTracker` guarda o que cada
   autopreenchimento escreveu; um campo só pode ser sobrescrito se estiver vazio ou se o valor
   atual for exatamente o que algum autofill colocou ali. Dois autofills que escrevem nos mesmos
   campos (CNPJ e CEP escrevem ambos no endereço) **precisam compartilhar o mesmo tracker**.
4. Mostre estado (`idle` / `loading` / `filled` / `error`) abaixo do campo, com botão de tentar
   de novo no erro.

---

## 6. Rotas, autenticação e permissão

Tudo em `App.tsx`. Três camadas de proteção, aninhadas:

```tsx
<Route path="/produtos" element={
  <RequireAuth>                    {/* tem accessToken? senão -> /login */}
    <FeatureGate code="Cardapio">  {/* usuário tem a feature? senão -> primeira tela permitida */}
      <AppShell><ProductsPage /></AppShell>
    </FeatureGate>
  </RequireAuth>
} />
```

- **`RequireAuth`** verifica o token e envolve tudo em `CompanyContextGate`.
- **`CompanyContextGate`** resolve empresa + filial ativas antes de renderizar a tela: busca
  `/api/companies/allowed` e `/api/workplaces`, seleciona a primeira válida, e bloqueia a
  renderização até ter um par (empresa, filial) autorizado. É o que garante que nenhuma tela
  monta sem tenant definido.
- **`FeatureGate code="X"`** usa `useMyFeatures()`. Os códigos são os mesmos do backend
  (`FeatureCodes.cs`): `Salao`, `Cardapio`, `Estoque`, `Equipe`, `Usuarios`, `Caixa`,
  `Faturamento`, `Preparo`, `Promocoes`, `Impressao`.
- O mapa `featurePath` em `features/access/hooks.ts` liga código de feature → rota. **Tela nova
  com feature nova precisa entrar nesse mapa**, senão o redirecionamento de "primeira tela
  permitida" não a encontra.
- `ManagerGate` restringe a `canManageAccess`.

Rota pública (sem nenhum gate): `/login`, `/cadastro`, `/pedido/:token`, `/cardapio/:branchIdParam`.

### authStore

`companyId`, `branchId`, `businessGroupId`, `employeeId`, tokens — persistido em
`localStorage` sob a chave `syncbar-auth`. Leia com seletor para evitar re-render desnecessário:

```ts
const accessToken = useAuthStore((s) => s.accessToken);
```

Fora de componente, use `useAuthStore.getState()`.

---

## 7. Design system — CSS puro com tokens

**Não há Tailwind em uso.** Existe um `tailwind.config.js` na raiz, mas ele é inválido (não tem
`export default`) e o pacote `tailwindcss` **não está instalado**. É lixo de uma tentativa
abandonada — não escreva classes utilitárias esperando que funcionem.

Todo o design system está em `src/styles/global.css`, com custom properties em `:root`.

### Tokens reais (use estes)

| Categoria | Tokens |
|---|---|
| Fundo | `--bg`, `--bg-raise`, `--bg-press` |
| Linha | `--line`, `--line-soft` |
| Texto | `--ink`, `--ink-dim`, `--ink-faint` |
| Marca | `--amber`, `--amber-deep`, `--amber-ink` |
| Status | `--free`, `--busy`, `--reserved`, `--closing`, `--blocked`, `--ok`, `--danger` |
| Tipografia | `--font-display`, `--font-cond`, `--font-body` |
| Forma | `--radius`, `--touch` (48px, alvo de toque) |
| Movimento | `--ease-standard`, `--ease-in-out`, `--duration-instant\|fast\|medium\|base\|entrance\|slow\|slower` |

### Tema: `data-theme`, não `prefers-color-scheme`

O tema é **escolha do usuário**, não do sistema operacional. `themeStore.ts` escreve
`document.documentElement.dataset.theme` e o CSS reage a `:root[data-theme="light"]`.
O padrão é **escuro**.

```css
/* ✅ certo */
.minha-coisa { background: var(--bg-raise); color: var(--ink); }
[data-theme="light"] .minha-coisa { border-color: var(--line-soft); }

/* ❌ errado — ignora a escolha do usuário */
@media (prefers-color-scheme: dark) { .minha-coisa { ... } }
```

⚠️ **`features/signup/SignupPage.css` viola isso hoje.** Ele usa um vocabulário de tokens que não
existe (`--ink-norm`, `--bg-base`, `--bg-faint`, `--primary`, `--primary-dark`) e reage a
`prefers-color-scheme`. Como os tokens não existem, todos os `var(..., fallback)` caem no
fallback — valores de tema claro — e a tela fica com títulos quase invisíveis quando o app está
no tema escuro. **Não copie esse arquivo como exemplo.** Ele precisa ser migrado para os tokens
reais e para `[data-theme]`.

### Acessibilidade

`ui/Field.tsx` é a referência: `useId()`, `htmlFor`, `aria-invalid`, `aria-describedby` ligando
hint e erro. Use `Field` / `TextField` / `SelectField` em vez de montar `<label>` + `<input>` na
mão. Estado assíncrono usa `role="status"`; erro usa `role="alert"`.

---

## 8. Testes

Playwright, em `test/features/<área>/`, espelhando `src/features/`.

```bash
npm run test:e2e
npm run test:e2e:ui
npm run test:e2e:storefront
```

Existem configs dedicadas: `playwright.config.ts` (padrão, sobe o dev server em :5173),
`playwright.storefront-devices.config.ts`, `.storefront-live.config.ts`, `.companies.config.ts`,
`.delivery.config.ts`, `.wizard.config.ts`.

**Seletores por `data-testid`.** Todo elemento interativo ou de verificação recebe um:

```tsx
<input id="cnpj" data-testid="cnpj" ... />
<span className="cnpj-status" data-testid="cnpj-status" role="status">
```

Não existe teste unitário de componente (sem Vitest/RTL). Tela nova é coberta por E2E.

---

## 9. Build e CI

O job `frontend` do `.github/workflows/ci.yml` roda:

```bash
npm ci
npm run build     # tsc -b && vite build
```

Não roda Playwright nem lint. Então: **erro de tipo quebra o CI, erro de comportamento não.**
Isso torna o `strict` do TypeScript a principal rede de segurança — não use `any` para calar o
compilador. Onde `any` já existe (`render={({ field }: any)` do react-hook-form), é dívida
conhecida, não exemplo a seguir.

Em produção o `nginx.conf` serve o SPA com fallback para `index.html` e faz proxy do backend.
Em desenvolvimento o proxy é do Vite:

```ts
proxy: { "/api": { target: "http://localhost:5250" }, "/uploads": { ... } }
```

⚠️ O proxy aponta para **HTTP :5250**. Se você subir a API no perfil HTTPS (`:7250`), o front
leva 502. Rode a API no perfil HTTP quando estiver testando pelo frontend.

---

## 10. Receita: tela nova

1. `src/features/<área>/api.ts` — funções tipadas usando `api<T>()`.
2. Tipos de resposta em `lib/types.ts` se forem compartilhados; locais ao `api.ts` se não forem.
3. `src/features/<área>/hooks.ts` — `useQuery` com `queryKey` contendo o escopo.
4. `src/features/<área>/<Área>Page.tsx` — a tela, usando `ui/` e `components/`.
5. Rota em `App.tsx`, com `RequireAuth` + `FeatureGate` + `AppShell`.
6. Se a feature for nova, adicionar o código em `featurePath` (`features/access/hooks.ts`) **e**
   no `FeatureAccessConvention` do backend.
7. Estilo com os tokens do `global.css`; CSS local só se for realmente específico da tela.
8. `data-testid` nos elementos que o E2E vai tocar.
9. Spec Playwright em `test/features/<área>/`.

---

## 11. Armadilhas conhecidas

1. **`tailwind.config.js` é inválido e o Tailwind não está instalado.** §7.
2. **`SignupPage.css` usa tokens inexistentes e `prefers-color-scheme`.** Causa títulos
   invisíveis no tema escuro. Não use como referência. §7.
3. **Máscara com `0` literal** no `react-input-mask` corrompe o valor silenciosamente. §5.
4. **Proxy do Vite aponta para HTTP :5250**, não HTTPS :7250. §9.
5. **Sem lint e sem teste unitário.** O gate é o `tsc`. §9.
6. **`global.css` tem ~57 KB em arquivo único.** Ao adicionar, agrupe por seção e comente; ao
   mexer em regra existente, confira se ela é usada por mais de uma tela.
7. **`test/routing.spec.ts` está vazio (0 byte).** Ou implemente, ou remova.
8. **Nome interno é "syncbar"** (`package.json`, chaves `syncbar-auth` / `syncbar-theme` no
   localStorage) enquanto o produto é NAME_PROJECT. Trocar as chaves desloga todo mundo — mude só
   com migração planejada.
9. **`queryKey` sem `companyId`** vaza cache entre empresas no seletor multi-tenant. §4.

---

## 12. Antes de abrir PR

- [ ] `npm run build` sem erro (é o gate do CI)
- [ ] Nenhum `fetch` direto — tudo via `api()` / `apiUpload()`
- [ ] `queryKey` inclui o escopo (companyId / branchId / usuário)
- [ ] Erro tratado por `ApiError.code`, não por texto da mensagem
- [ ] Cores e espaçamentos vindos dos tokens do `global.css`
- [ ] Tema claro conferido via `[data-theme="light"]` (não via SO)
- [ ] `data-testid` nos elementos interativos
- [ ] Rota nova protegida por `RequireAuth` + `FeatureGate`
- [ ] Feature nova registrada em `featurePath` e no backend
- [ ] Sem `any` novo

## Menu lateral — MUI e Motion

`InterfaceProvider` conecta Material UI à escolha de tema do `themeStore`, com
identidade âmbar e localização pt-BR. Configura `LazyMotion`/`MotionConfig` com
movimento reduzido. Não aplica CssBaseline sobre os componentes legados.

`AppShell` usa Drawer esquerdo de 256px (ícones e nomes) ou 80px (ícones com
Tooltip e nome acessível). A chave `NAME_PROJECT-sidebar-collapsed` guarda a escolha,
sem alterar as chaves de autenticação. Abaixo de 900px, usa Drawer temporário
com nomes, fechamento por Escape e retorno de foco ao botão de abertura.
Empresa/filial e alertas continuam no cabeçalho. Os links acompanham os gates
reais em `App.tsx`; rotas públicas, tablet e garçom continuam sem AppShell.

As transições de largura duram 180ms e a entrada de conteúdo usa Motion com
fade de 160ms, sem deslocamento que interfira com painéis fixos. Movimento
reduzido desativa essas animações. O CSS de layout está em `AppShell.css`.

`test/features/navigation/sidebar.spec.ts` verifica persistência, nomes no modo
compacto, rota ativa, temas, navegação móvel, logout e permissões com API simulada.
