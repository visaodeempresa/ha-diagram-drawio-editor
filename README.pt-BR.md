# Draw.io Editor para Home Assistant

Draw.io Editor é uma custom integration para Home Assistant que embute o editor diagrams.net em um painel do Home Assistant, permite abrir arquivos `.drawio` a partir de botões Lovelace e pode gerar um arquivo `.png` irmão sempre que o diagrama for salvo.

## O que este repositório entrega

- Custom integration do Home Assistant para HACS.
- Painel frontend em TypeScript compilado como módulo estático do Home Assistant.
- Flags de feature para rollout controlado:
  - `enable_panel`
  - `enable_open_file`
  - `enable_query_open`
  - `enable_save`
  - `enable_png_export`
- GitHub Actions para validação de build TypeScript, compilação Python, validação HACS e hassfest.
- Documentação em inglês e português do Brasil.

## Observação importante de implementação

O repositório não pode ser puramente TypeScript porque custom integrations do Home Assistant precisam de uma camada backend em Python para registrar o painel, proteger o acesso a arquivos e persistir os arquivos `.drawio` e `.png`. O editor frontend em si foi implementado em TypeScript.

## Instalação

### Repositório customizado no HACS

1. Adicione este repositório como custom repository no HACS com a categoria `Integration`.
2. Não selecione `Dashboard`. Este repositório tem uma camada backend do Home Assistant e foi publicado para a categoria `Integration`.
3. Instale `Draw.io Editor`.
4. Reinicie o Home Assistant.
5. Adicione a integração em `Settings > Devices & Services`.

### Instalação local para desenvolvimento

1. Copie `custom_components/ha_drawio_editor` para o diretório `custom_components` do seu Home Assistant.
2. Execute `npm ci`.
3. Execute `npm run build`.
4. Reinicie o Home Assistant.
5. Adicione a integração em `Settings > Devices & Services`.

## Campos da configuração inicial

- `storage_path`: raiz relativa de armazenamento dentro do diretório de configuração do Home Assistant.
- `panel_url_path`: segmento de URL do painel customizado.
- `sidebar_title`: rótulo na barra lateral.
- `sidebar_icon`: identificador do Material Design Icons.
- `editor_url`: URL embed do diagrams.net ou uma URL self-hosted compatível.
- `default_diagram_path`: caminho relativo opcional do diagrama aberto automaticamente quando o painel carrega.

Não use URLs estáticas do Home Assistant como `/local/...` em `default_diagram_path`. Esse campo aceita apenas um caminho relativo dentro do `storage_path` configurado, por exemplo `samples/mapa-vertical-2D_v2.drawio`.

## Rollout recomendado

1. Habilite apenas `enable_panel`.
2. Verifique se o editor renderiza dentro do Home Assistant.
3. Habilite `enable_open_file` e `enable_query_open`.
4. Teste a abertura de arquivos por botões de navegação Lovelace.
5. Habilite `enable_save`.
6. Confirme a persistência do `.drawio`.
7. Habilite `enable_png_export`.
8. Confirme a geração do `.png` irmão ao lado do diagrama.

## Exemplos de uso

### Abrir um diagrama existente a partir de um botão Lovelace

Veja [examples/button-open-diagram.yaml](examples/button-open-diagram.yaml).

### Abrir automaticamente o mapa residencial de exemplo ao carregar o painel

A integração provisiona `samples/mapa-vertical-2D_v2.drawio` para a raiz de armazenamento configurada na inicialização, desde que o arquivo ainda não exista.

Defina `default_diagram_path` como `samples/mapa-vertical-2D_v2.drawio` e abra o painel Draw.io pela barra lateral do Home Assistant.

Veja [examples/direct-panel-mapa-vertical-2D_v2.yaml](examples/direct-panel-mapa-vertical-2D_v2.yaml).

### Abrir um caminho que será criado no primeiro salvamento

Veja [examples/button-create-or-edit-diagram.yaml](examples/button-create-or-edit-diagram.yaml).

### Colar uma stack Lovelace pronta para o primeiro uso

Veja [examples/lovelace-quick-start.yaml](examples/lovelace-quick-start.yaml).

## Desenvolvimento

```bash
npm ci
npm run lint
npm run build
python -m compileall custom_components
```

## Documentação adicional

- Arquitetura em inglês: [docs/architecture.md](docs/architecture.md)
- Arquitetura em português: [docs/architecture.pt-BR.md](docs/architecture.pt-BR.md)
- Referências em inglês: [docs/references.md](docs/references.md)
- Referências em português: [docs/references.pt-BR.md](docs/references.pt-BR.md)
