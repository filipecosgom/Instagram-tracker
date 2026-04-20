# Changelog — Instagram Tracker Updates

## Bugs corrigidos

### Bug crítico no selector de snapshots
**Ficheiro:** `assets/dashboard.js`  
**Linha:** 13  
**Problema:** `updateDetail()` tentava aceder `DATA[idx]` em vez de `DATA.snapshots[idx]`, causando erro quando o utilizador mudava de snapshot no selector.  
**Corrigido:** Alterado para `DATA.snapshots[idx]`.

### Duplicação de constantes no config
**Ficheiro:** `src/config.py`  
**Problema:** `FOLLOWERS_FILE` e `MASTER_FILE` apontavam ambos para `snapshots/master_followers.json`, mas `load_master()` esperava lista e `load_followers_dict()` esperava dicionário. Conflito de tipos.  
**Corrigido:** Removida constante `MASTER_FILE` (não é usada).

### Código morto em storage
**Ficheiro:** `src/storage.py`  
**Problema:** Funções `load_master()` e `save_master()` nunca são chamadas no pipeline actual.  
**Corrigido:** Funções removidas.

---

## Novas features

### 1. Dois conjuntos de stats cards
**Ficheiro:** `assets/dashboard.js`

Agora o dashboard mostra dois painéis de estatísticas:

**"This week"** — compara último snapshot com o anterior:
- Total followers (do último snapshot)
- Gained (desde o snapshot anterior)
- Lost (desde o snapshot anterior)
- Net change (desde o snapshot anterior)

**"Since tracking started"** — compara `master_followers.json` com início do tracking:
- Active followers (total actualmente activos)
- Total gained (todos os seguidores que alguma vez te seguiram)
- Total lost (todos os que deixaram de seguir)
- Net growth (saldo final: activos menos perdidos)

### 2. Lista completa de seguidores activos
**Ficheiro:** `assets/dashboard.js`, `assets/style.css`

Nova secção "All active followers" abaixo das tabelas de gained/lost.

- Mostra todos os seguidores com `status: "active"` no `master_followers.json`
- Grid de 3 colunas (vs 2 colunas nas tabelas de gained/lost)
- Máx. height 400px com scroll
- Usernames clicáveis com tooltips

### 3. Tooltips com histórico de seguidor
**Ficheiro:** `assets/dashboard.js`

Ao fazer hover sobre qualquer username na lista de seguidores activos, aparece tooltip com:
- First seen: data da primeira vez que te seguiu
- Last seen: data do último snapshot onde apareceu

Dados vêm do campo `first_seen` e `last_seen` em `master_followers.json`.

### 4. Remoção de suporte a profile images
**Ficheiro:** `assets/dashboard.js`, `assets/style.css`

A Meta não exporta imagens de perfil nos ZIPs, portanto o código que tentava renderizar avatares foi removido:
- Removida lógica de `profileImage` em `renderUserList()`
- Removidos estilos `.uimg` do CSS
- Usernames aparecem apenas como `@username` clicável

---

## Ficheiros alterados

```
src/
  config.py        ← MASTER_FILE removido
  storage.py       ← load_master/save_master removidos

assets/
  dashboard.js     ← bug fix + dual stats + followers section + tooltips
  style.css        ← followers-section styles + grid 3 colunas
```

---

## Como actualizar o teu repositório

1. Substitui `src/config.py` e `src/storage.py` pelas versões corrigidas
2. Substitui `assets/dashboard.js` e `assets/style.css` pelas versões actualizadas
3. Testa com `python main.py`

Todos os ficheiros mantêm compatibilidade com a estrutura de dados existente — não precisas de reprocessar snapshots.
