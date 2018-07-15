# Resultados do TPS 2017

Durante o Teste Público de Segurança do Sistema Eletrônico de Votação de 2017, encontramos
vulnerabilidades que permitiam **execução de código arbitrário** na Urna Eletrônica.

## Conteúdo deste repositório

### Palestra técnica

 * [Slides](https://epicleet.github.io/tps2017/apresentacao/slides.pdf) da palestra técnica
   com nossos relatos dos testes.

### Cifragem e decifragem do sistema de arquivos

O cartão de carga da urna utiliza o sistema de arquivos `ueminix` (customizado pelo TSE),
que ofusca o conteúdo dos arquivos cifrando-os com AES-XTS.

Disponibilizamos aqui dois utilitários relacionados a esse sistema de arquivos:

 * [encall.py](fs_crypto/encall.py): cifra os arquivos originais, criando um diretório `enc`
   com os arquivos cifrados.

 * [decall.py](fs_crypto/decall.py): decifra os arquivos do diretório `enc`, criando um
   diretório `dec` com todos os arquivos decifrados.

Note que é necessário fornecer a imagem do disco (`dsk.img`), por dois motivos:

 * O *padding* da cifra não pode ser lido diretamente a partir do espaço de usuário,
   portanto lemos da imagem de disco.

 * Uma das chaves do AES-XTS está contida no segundo setor da partição, e é recuperada
   pelos próprios utilitários.

A outra chave do AES-XTS pode ser recuperada do código do `ueminix` no kernel, e deve ser
configurada diretamente no código fonte dos utilitários (variável `key1`). Sem acesso ao
código fonte, essa chave poderia ser obtida através de engenharia reversa do bootloader e
do kernel decifrado (ver
[relatório feito pelo TSE](https://epicleet.github.io/tps2017/relatorios/tse/relatorioTPS2017.pdf#page=8)).

### Alteração de votos na urna

O arquivo [exploit.py](exploit/exploit.py) ilustra o ataque que propomos para
alterar votos na urna. Infectamos a biblioteca [hkdf](exploit/hkdf.cpp) com um
código que, por sua vez, infecta o espaço de memória do executável
[vota](exploit/gui/infoeleitor.cpp) (software de votação).

Os trechos de código do [hkdf](exploit/hkdf.cpp) e do [vota](exploit/gui/infoeleitor.cpp) replicam
a estrutura do software original da urna eletrônica, permitindo simular o ataque em um
modelo simplificado muito próximo do sistema real.

Para executar o simulador do software de votação, entre no diretório `exploit` e execute
`make test_cli` para iniciar o simulador modo texto, ou `make test_gui` para iniciar
o simulador gráfico.

Para infectar a biblioteca, instale o [pwntools](https://github.com/Gallopsled/pwntools#installation)
e execute `make exploit_cli` para comprometer o simulador modo texto, ou
`make exploit_gui` para comprometer o simulador modo gráfico.

Depois disso, ao executar novamente o simulador do software de votação, você observará que
os votos foram alterados.

### Fluxo de um ataque real

Um ataque real seguiria o seguinte fluxo:

1. Obteríamos a imagem com o conteúdo de uma mídia de carga
2. Faríamos engenharia reversa no bootloader e no kernel decifrado para obter a
chave que cifra/decifra os outros arquivos da mídia de carga
3. Decifraríamos o sistema de arquivos
4. Executaríamos o exploit para infectar o arquivo `libhkdf.so` original
5. Cifraríamos novamente para gerar uma mídia de carga modificada

## Sobre a equipe

Nossa equipe é composta por membros do [ELT](https://ctftime.org/team/9061), time
interinstitucional que participa de competições de CTF. Conheça também o
[Pwn2Win](https://pwn2win.party), competição organizada anualmente por nós.
