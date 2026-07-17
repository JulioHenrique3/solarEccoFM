# SolarEcchoFM

SolarEcchoFM é um bot de música para Discord desenvolvido em Python. A base do projeto foi criada por [@DuneGG](https://www.youtube.com/@DuneDiscord) e pode ser conferida na série de tutoriais linkada abaixo. Este repositório contém a versão com correções de execução e adaptações.

---

> [!IMPORTANT]
> **📺 Pré-requisito de Aprendizado — Tutoriais do DUNEGG**
>
> Antes de configurar, modificar ou contribuir com este projeto, **é obrigatório seguir a série de tutoriais do canal [@DuneDiscord](https://www.youtube.com/@DuneDiscord) no YouTube.** Os vídeos cobrem toda a base conceitual necessária — criação do bot no Developer Portal, estrutura de Cogs, comandos slash e transmissão de áudio — sem os quais partes do código podem ser mal interpretadas ou configuradas incorretamente.
>
> Siga os vídeos abaixo na ordem indicada:
>
> * 🎬 **Aula 1 — Criando um Bot no Discord:** [Assistir no YouTube](https://www.youtube.com/watch?v=TS4wt3LfDlo&list=PL9-YiBpH1Ne7NJlG9wGsEee24koLc8JTT)
> * 🎬 **Aula 7 — Criando um Bot de Música (Base do Projeto):** [Assistir no YouTube](https://www.youtube.com/watch?v=f8AyaXH_8A4&list=PL9-YiBpH1Ne7NJlG9wGsEee24koLc8JTT&index=7)
> * 📺 **Canal completo:** [@DuneDiscord no YouTube](https://www.youtube.com/@DuneDiscord)

> [!CAUTION]
> **🚫 AVISO CRÍTICO — NÃO HOSPEDE ESTE BOT EM SERVIÇOS DE NUVEM DO DISCORD**
>
> Este projeto foi desenvolvido para rodar **100% localmente na máquina do usuário**. Hospedar este bot em serviços de nuvem que se integram diretamente à plataforma do Discord (como bots que rodam em servidores terceiros de forma automatizada, ou serviços que violam os [Termos de Serviço do Discord](https://discord.com/terms)) **representa risco real de ban permanente do bot e/ou da conta do usuário responsável.**
>
> ✅ **Modo correto de uso:** Execute o bot localmente com `python main.py` no seu próprio computador.
> ❌ **Não faça:** Subir o token do bot para plataformas de hospedagem não homologadas pelo Discord.
>
> *Futuramente, uma nova arquitetura vinculada a um servidor próprio será avaliada para operação contínua (24h/dia), seguindo todas as diretrizes oficiais da plataforma.*

---

## Índice

- [Estrutura de Arquivos e Diretórios](#estrutura-de-arquivos-e-diretórios)
- [Dependências Externas (Sistema)](#dependências-externas-sistema)
- [Ambiente Virtual (venv) e Instalação](#ambiente-virtual-venv-e-instalação)
  - [Criando o Ambiente Virtual](#criando-o-ambiente-virtual)
  - [Ativando o Ambiente Virtual](#ativando-o-ambiente-virtual)
  - [Instalando as Dependências de Python](#instalando-as-dependências-de-python)
- [Configuração do Arquivo `.env`](#configuração-do-arquivo-env)
- [Bibliotecas e Ferramentas Utilizadas](#bibliotecas-e-ferramentas-utilizadas)
  - [discord.py](#discordpy)
  - [yt-dlp](#yt-dlp)
  - [PyNaCl e audioop-lts](#pynacl-e-audioop-lts)
  - [python-dotenv](#python-dotenv)
- [Documentações Técnicas](#documentações-técnicas)

---

## Estrutura de Arquivos e Diretórios

```text
solarEcchoFM/
├── cogs/                 # Diretório contendo os módulos (cogs) do bot
│   ├── MUSIC.md          # Documentação detalhada da lógica de music.py
│   └── music.py          # Lógica de reprodução de áudio e comandos de música
├── venv/                 # Diretório do Ambiente Virtual (isolamento de pacotes)
├── .env                  # Chaves e tokens sensíveis de configuração
├── main.py               # Arquivo principal para inicialização e conexão do bot
├── MAIN.md               # Documentação detalhada da lógica de main.py
├── requirements.txt      # Dependências Python necessárias para execução
└── README.md             # Instruções gerais de configuração (este arquivo)
```

---

## Dependências Externas (Sistema)

Para que o bot transmita áudio para os canais de voz do Discord, é estritamente obrigatório que a ferramenta **FFmpeg** esteja instalada e configurada no Path do sistema operacional.

*   **Linux (Ubuntu/Debian)**:
    ```bash
    sudo apt update && sudo apt install ffmpeg
    ```
*   **macOS (via Homebrew)**:
    ```bash
    brew install ffmpeg
    ```
*   **Windows**:
    1. Baixe os arquivos executáveis compilados no site oficial do [FFmpeg (gyan.dev)](https://www.gyan.dev/ffmpeg/builds/).
    2. Extraia os arquivos e adicione a pasta `bin` (que contém o arquivo `ffmpeg.exe`) às Variáveis de Ambiente do Sistema (PATH).

---

## Ambiente Virtual (venv) e Instalação

O Ambiente Virtual (`venv`) isola as bibliotecas instaladas neste projeto do restante do sistema operacional, prevenindo conflitos de versão.

### Criando o Ambiente Virtual

Abra o terminal na pasta raiz do projeto e execute:

```bash
python -m venv venv
```
*(No Linux/macOS, pode ser necessário usar `python3` ao invés de `python`)*.

### Ativando o Ambiente Virtual

*   **Linux / macOS (Bash/Zsh)**:
    ```bash
    source venv/bin/activate
    ```
*   **Windows (PowerShell)**:
    ```powershell
    venv\Scripts\Activate.ps1
    ```
*   **Windows (Prompt de Comando - CMD)**:
    ```cmd
    venv\Scripts\activate.bat
    ```

Quando ativado, o prefixo `(venv)` aparecerá no início da linha de comando do terminal.

### Instalando as Dependências de Python

Com o `venv` ativo, execute o comando abaixo para instalar todos os pacotes necessários:

```bash
pip install -r requirements.txt
```

---

## Configuração do Arquivo `.env`

Crie um arquivo texto na raiz do projeto chamado `.env` e defina as seguintes chaves de configuração com os seus respectivos valores obtidos no [Discord Developer Portal](https://discord.com/developers/applications):

```env
DISCORD_TOKEN=TokenSecretoDoSeuBotAqui
BOT_ID=IDNumericoDoSeuBotAqui
```

*   `DISCORD_TOKEN`: A chave privada de autenticação do bot usada para conectá-lo à rede do Discord.
*   `BOT_ID`: O ID único da aplicação do bot (necessário para registrar os comandos de barra slash).

---

## Bibliotecas e Ferramentas Utilizadas

Abaixo estão detalhadas as tecnologias utilizadas por este bot:

### `discord.py`
Interface em Python para se conectar com a API do Discord.
*   **`discord.ext.commands`**: Submódulo para definição de Cogs e comandos tradicionais.
*   **`discord.app_commands`**: Submódulo para registrar comandos slash (`/`) nativos do Discord.

### `yt-dlp`
Bifurcação ativa do `youtube-dl`. É usada exclusivamente para fazer a busca de termos no YouTube e extrair o link de streaming direto do áudio (sem necessidade de fazer o download do arquivo de vídeo localmente).

### `PyNaCl` e `audioop-lts`
Bibliotecas necessárias para o processamento de canais de voz do Discord.
*   **`PyNaCl`**: Provê as funções criptográficas exigidas pelo protocolo de voz do Discord.
*   **`audioop-lts`**: Correção de compatibilidade para o Python 3.13+. O submódulo nativo `audioop` foi descontinuado e removido do Python Standard Library, exigindo o pacote `audioop-lts` para a decodificação/modulação do fluxo de bytes PCM.

### `python-dotenv`
Lê o arquivo `.env` localizado na raiz do projeto e carrega as variáveis definidas para o ambiente de execução Python (`os.environ`), isolando as chaves do código fonte.

---

## Documentações Técnicas

Para explicações detalhadas sobre a lógica de programação de cada arquivo, classes, métodos e comandos, acesse os arquivos de documentação técnica:

*   **[Documentação do `main.py`](./MAIN.md)**: Explicação detalhada da inicialização e sincronização.
*   **[Documentação do `cogs/music.py`](./cogs/MUSIC.md)**: Detalhamento da lógica de fila, conexão de áudio e manipulação do FFmpeg.
