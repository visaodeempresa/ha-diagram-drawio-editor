# Arquitetura

## Objetivo

Este projeto embute o editor diagrams.net dentro de um painel customizado do Home Assistant e mantém as operações de arquivo dentro do próprio Home Assistant. Quando o salvamento está habilitado, a integração grava o XML `.drawio` e também pode gravar um arquivo `.png` irmão com o mesmo nome-base.

## Componentes

### Custom integration do Home Assistant

- Registra config entry e options flow.
- Controla as flags de rollout.
- Serve o bundle frontend compilado como módulo estático.
- Registra o painel customizado.
- Expõe comandos WebSocket autenticados para configuração de runtime, leitura e gravação de diagramas.
- Valida que todos os caminhos permanecem dentro da raiz de armazenamento configurada.

### Painel frontend em TypeScript

- Executa como web component de painel customizado do Home Assistant.
- Embute `https://embed.diagrams.net` ou uma URL compatível informada pelo usuário dentro de um iframe.
- Implementa o protocolo JSON do diagrams.net.
- Carrega um arquivo `.drawio` a partir do Home Assistant quando a abertura está habilitada.
- Solicita a exportação PNG ao editor antes de persistir o salvamento quando a exportação PNG está habilitada.

## Modelo de rollout

O repositório foi construído propositalmente em torno de flags isoladas:

- `enable_panel`
- `enable_open_file`
- `enable_query_open`
- `enable_save`
- `enable_png_export`

Progressão recomendada:

1. Habilitar apenas `enable_panel` para validar a renderização do painel.
2. Habilitar `enable_open_file` e `enable_query_open` para abrir arquivos a partir de botões Lovelace.
3. Habilitar `enable_save`.
4. Habilitar `enable_png_export`.

## Caminho de salvamento e comportamento do PNG

- A raiz de armazenamento é relativa ao diretório de configuração do Home Assistant.
- O caminho do diagrama deve permanecer dentro dessa raiz.
- As extensões suportadas são `.drawio` e `.xml`.
- O caminho do PNG irmão é gerado com `Path.with_suffix(".png")`.
- O frontend atualmente exporta a página atual para um único PNG porque o requisito pede um PNG irmão por caminho de diagrama.

## Modelo de segurança

- O painel customizado é registrado apenas para administradores.
- A API WebSocket é exclusiva para administradores.
- Os caminhos são normalizados e qualquer tentativa de sair da raiz configurada é rejeitada.
- O frontend aceita mensagens `postMessage` apenas da origem do editor configurado.

## Pontos naturais de extensão

- diagrams.net self-hosted pode ser habilitado alterando a URL do editor durante a configuração.
- Regras de exportação multipágina podem ser estendidas na requisição de export do frontend.
- Pickers de arquivo adicionais ou entradas baseadas em entidades podem ser acrescentados sobre o fluxo atual de abertura por query string.

