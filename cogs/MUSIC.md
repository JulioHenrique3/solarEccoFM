# Explicação Técnica do Código: `cogs/music.py`

Este documento detalha o comportamento técnico das classes, métodos, parâmetros, variáveis e lógica de programação presentes no arquivo `cogs/music.py`.

---

## Estrutura da Classe e Inicialização

```python
class music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.is_playing = False
        self.music_queue = []
        self.YDL_OPTIONS = {
            'format': 'bestaudio', 
            'noplaylist': 'True',
            'cookiesfrombrowser': ('brave',),
            'remote_components': ['ejs:npm', 'ejs:github']
        }
        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
            'options': '-vn'
        }
        self.vc = ""
```

*   **Classe `music`**: Herda de `commands.Cog`. Esta herança permite modularizar o código do bot, agrupando comandos e ouvintes de voz em uma única unidade estrutural carregável pelo `main.py`.
*   **Método `__init__(self, client)`**:
    *   `self.client`: Armazena a referência para a instância global do bot (`bot` criada no `main.py`), permitindo acessar dados de rede, cache e usuários.
    *   `self.is_playing`: Booleano (`True`/`False`) de controle de estado. Indica se existe um fluxo de áudio ativo sendo transmitido para o canal de voz.
    *   `self.music_queue`: Uma lista (2D) dinâmica de controle de fila. Cada entrada na lista é outra lista contendo `[dados_da_musica, canal_de_voz]`.
    *   `self.YDL_OPTIONS`: Dicionário com diretivas de busca e extração passadas para o objeto `YoutubeDL`.
        *   `'format': 'bestaudio'`: Instrui a extração a obter apenas o melhor fluxo de áudio disponível, reduzindo o tráfego de dados.
        *   `'noplaylist': 'True'`: Impede o processamento em lote de listas de reprodução inteiras quando um link de playlist é fornecido.
        *   `'cookiesfrombrowser': ('brave',)`: Extrai os cookies do perfil de navegação do Brave para evitar bloqueios de bots por parte da CDN do YouTube.
    *   `self.FFMPEG_OPTIONS`: Dicionário com flags de linha de comando para o processo do executável FFmpeg.
        *   `'before_options'`: Parâmetros passados antes de definir o arquivo de entrada. `-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5` forçam o FFMpeg a tentar restabelecer conexões TCP/HTTP caso ocorra perda de pacotes ou quedas temporárias de streaming.
        *   `'options': '-vn'`: Desabilita a decodificação do fluxo de vídeo, limitando a execução à faixa de áudio.
    *   `self.vc`: String (posteriormente atualizada para uma instância de `VoiceClient`). Gerencia o estado e as chamadas da conexão de voz ativa do bot.

---

## Métodos Internos de Áudio

### `search_yt(self, item)`
```python
def search_yt(self, item):
    with YoutubeDL(self.YDL_OPTIONS) as ydl:
        try: 
            info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
        except Exception: 
            return False
    return {'source': info['url'], 'title': info['title']}
```
*   **Função**: Realiza a busca de termos no YouTube e recupera a URL direta de streaming do arquivo de áudio.
*   **Parâmetro `item`**: String contendo o termo de pesquisa ou a URL direta do vídeo.
*   **Lógica**:
    *   `YoutubeDL(self.YDL_OPTIONS)`: Instancia o extrator com as configurações definidas.
    *   `ydl.extract_info("ytsearch:%s" % item, download=False)`: Aplica o prefixo de busca `ytsearch:`. A opção `download=False` extrai os metadados do vídeo da API do YouTube sem gravar nenhum arquivo local no disco rígido.
    *   `['entries'][0]`: A busca retorna uma lista de resultados. Extrai-se o primeiro vídeo correspondente (`índice 0`).
    *   **Retorno**: Se ocorrer qualquer erro na extração, captura a exceção e retorna `False`. Se bem-sucedido, retorna um dicionário contendo o endereço final do streaming de áudio (`'source'`) e a string contendo o título do vídeo (`'title'`).

### `play_next(self)`
```python
def play_next(self):
    if len(self.music_queue) > 0:
        self.is_playing = True
        m_url = self.music_queue[0][0]['source']
        self.music_queue.pop(0)
        self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
    else:
        self.is_playing = False
```
*   **Função**: Gerencia a transição recursiva de faixas de áudio na fila.
*   **Lógica**:
    *   Verifica se o tamanho (`len`) de `self.music_queue` é maior que 0.
    *   `m_url`: Extrai a URL direta de streaming do primeiro elemento da fila.
    *   `self.music_queue.pop(0)`: Remove o primeiro elemento da lista de fila, deslocando os demais índices à esquerda.
    *   `self.vc.play(...)`: Aciona o pipeline de voz do Discord. Instancia `discord.FFmpegPCMAudio` que abre um subprocesso ffmpeg localmente para ler o fluxo `m_url` e convertê-lo em pacotes de áudio síncronos.
    *   `after=lambda e: self.play_next()`: Executa uma função anônima lambda quando a faixa atual termina. Ela chama `play_next()` novamente, reiniciando o ciclo de checagem de fila.

### `play_music(self)`
```python
async def play_music(self):
    if len(self.music_queue) > 0:
        self.is_playing = True
        m_url = self.music_queue[0][0]['source']
        
        if self.vc == "" or not self.vc.is_connected() or self.vc == None:
            self.vc = await self.music_queue[0][1].connect()
        else:
            await self.vc.move_to(self.music_queue[0][1])
        
        print(self.music_queue)
        self.music_queue.pop(0)
        self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
    else:
        self.is_playing = False
        await self.vc.disconnect()
```
*   **Função**: Conecta o bot ao canal de voz apropriado e inicia a primeira faixa da fila.
*   **Lógica**:
    *   Checa se `self.vc` está vazio, desconectado ou nulo. Se verdadeiro, estabelece a conexão WebSocket de voz chamando `.connect()` no objeto de canal (`VoiceChannel`) armazenado em `self.music_queue[0][1]`, retornando o controlador de voz (`VoiceClient`) para `self.vc`.
    *   Se já estiver conectado em outro canal do servidor, executa `await self.vc.move_to(...)` migrando a conexão de voz do bot para o novo canal.
    *   Retira o elemento atual da fila com `.pop(0)`.
    *   Inicializa a reprodução de áudio via `self.vc.play(...)` e define o callback para `play_next()`.
    *   Se a fila estiver vazia no momento em que for executado, desconecta o bot do canal chamando `await self.vc.disconnect()`.

---

## Comandos de Barra (Slash Commands)

### `/ajuda`
```python
@app_commands.command(name="ajuda", description="Mostre um comando de ajuda.")
async def help(self, interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    helptxt = "..."
    embedhelp = discord.Embed(colour=1646116, title=..., description=helptxt)
    # ...
    await interaction.followup.send(embed=embedhelp)
```
*   **Decorador `@app_commands.command`**: Registra o método como um comando slash.
*   **`interaction: discord.Interaction`**: Parâmetro contendo a representação de contexto da interação gerada no Discord (dados do usuário, canal, estado).
*   **`interaction.response.defer(thinking=True)`**: Adia a resposta da API do Discord. O Discord exige uma resposta em menos de 3 segundos para comandos slash. Com o `defer`, o bot sinaliza que está processando em segundo plano (mostrando "O bot está pensando...") estendendo o tempo limite de resposta para 15 minutos.
*   **`discord.Embed`**: Construtor do layout visual de mensagens.
    *   `colour=1646116`: Define a cor da barra lateral esquerda do embed usando notação numérica (inteiro correspondente ao código hexadecimal).
*   **`interaction.followup.send(embed=embedhelp)`**: Envia a resposta final para o usuário usando o webhook de acompanhamento.

### `/play`
```python
@app_commands.command(name="play", description="Toca uma música do YouTube.")
@app_commands.describe(busca="Digite o nome da música no YouTube")
async def play(self, interaction: discord.Interaction, busca: str):
```
*   **`@app_commands.describe(...)`**: Adiciona metadados visuais de ajuda ao parâmetro no menu de comandos do próprio Discord.
*   **Parâmetro `busca: str`**: String digitada pelo usuário contendo o termo de busca ou link.
*   **Lógica**:
    *   Obtém o canal de voz do usuário chamando `interaction.user.voice.channel`. Se o usuário não estiver em um canal, o acesso a esse atributo gera uma exceção (capturada no bloco `except`), respondendo que o usuário deve primeiro conectar-se a um canal.
    *   Invoca `self.search_yt(query)`. Se o retorno for um booleano (`True`), indica falha e responde com um embed de erro.
    *   Se o retorno for o dicionário contendo os dados do áudio, cria um embed de sucesso e adiciona `[song, voice_channel]` em `self.music_queue`.
    *   Se `self.is_playing == False`, chama `await self.play_music()` para iniciar a reprodução.

### `/fila`
```python
@app_commands.command(name="fila", description="Mostra as atuais músicas da fila.")
async def q(self, interaction: discord.Interaction):
```
*   **Lógica**: Itera sobre a matriz `self.music_queue` de `0` até o comprimento final da lista (`len`). Lê o valor da chave `'title'` dentro de `self.music_queue[i][0]` para formatar uma string numerada com todas as faixas enfileiradas. Se a string estiver vazia, retorna que não há músicas na fila.

### `/pular`
```python
@app_commands.command(name="pular", description="Pula a atual música que está tocando.")
@app_commands.default_permissions(manage_channels=True)
async def pular(self, interaction: discord.Interaction):
```
*   **Decorador `@app_commands.default_permissions(...)`**: Filtra no cliente do Discord para que apenas membros com a permissão "Gerenciar Canais" (`manage_channels=True`) tenham permissão para ver e executar o comando slash.
*   **Lógica**: Executa `self.vc.stop()`. Isso cancela o fluxo de decodificação do FFMpeg atual, o que dispara automaticamente a execução do callback assinado no parâmetro `after` em `self.vc.play()` (que é o `play_next()`), avançando a fila de música.

### `@pular.error` (Manipulador de Erro do Comando)
```python
@pular.error
async def skip_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, commands.MissingPermissions):
        # ...
    else:
        raise error
```
*   **Decorador `@pular.error`**: Trata erros de execução originados especificamente no comando `pular`.
*   **Parâmetros**:
    *   `error`: Objeto contendo os metadados do erro disparado.
*   **Lógica**: Checa se a classe do erro condiz com `commands.MissingPermissions` (quando um usuário burlar a UI ou forçar a execução sem a permissão exigida). Se sim, envia um embed informando que falta a permissão necessária. Se o erro for outro, relança o erro usando `raise error` para que o log padrão o registre.

### `/pausar`
*   **Lógica**: Verifica se `self.vc` existe e se `self.vc.is_playing()` retorna `True`. Em caso positivo, interrompe temporariamente o fluxo de áudio chamando `self.vc.pause()`.

### `/retomar`
*   **Lógica**: Verifica se `self.vc` existe e se `self.vc.is_paused()` retorna `True`. Em caso positivo, reinicia o fluxo de áudio interrompido chamando `self.vc.resume()`.

---

## Ponto de Carregamento Assíncrono (`setup`)

```python
async def setup(client):
    await client.add_cog(music(client))
```
*   **Função**: Corrotina global requerida pela API do `discord.py` ao chamar `bot.load_extension()`.
*   **Parâmetro `client`**: A instância do bot enviada pelo `main.py`.
*   **Lógica**: Registra a classe `music` na árvore de cogs do bot usando o método `await client.add_cog()`.
