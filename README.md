## Analisador de Estatísticas de Mapas para Rainbow Six Siege

Olá, operadores! 🖱️💻🎮

Já se perguntou como você e/ou sua squad se saem nos diferentes mapas ranqueados do Rainbow Six Siege? Já quis saber em quais mapas você é o verdadeiro GOAT, o próximo Nesk, e aqueles onde... você se parece mais com um bagre? 😂 Quer descobrir em quais mapas sua squad parece estar sem sinergia, coordenação, entregando mais que o Sedex 📫 e começar a banir esses mapas? ⛔ Tenho a ferramenta perfeita para você!

Esta é uma ferramenta em Python que analisa detalhadamente o seu desempenho em cada mapa ranqueado. Utilizando a API siegeapi do CNDRD, ela extrai as estatísticas dos jogadores e calcula taxas de vitória, KD (Kill/Death) e KOST (Kill/Objetive/Survive/Trade), dando a você uma visão de como você e/ou sua squad performam em cada mapa. 

E a melhor parte? Você não precisa ser um expert em Python para usar! O programa pode ser aberto diretamente, sem a necessidade de ter o Python instalado no seu sistema. O executável já inclui todas as dependências e o interpretador necessário. Então, o que está esperando? Vamos aprofundar nessas estatísticas e elevar o seu jogo! 📈

## Como usar? 🤔
1. Baixe o repositório [R6MapStats](https://github.com/RhuanToneto/R6MapStats/archive/refs/heads/main.zip).
2. Extraia o conteúdo do arquivo ZIP baixado para a pasta de sua escolha.
3. Navegue até a pasta onde você extraiu os arquivos.
4. Execute o arquivo `R6MapStats.exe` clicando duas vezes nele.
   - Mantenha a pasta do repositório em um local seguro. Recomendo criar um atalho para o executável na área de trabalho para facilitar o acesso. Não copie e nem mova o executável diretamente para a área de trabalho. Lembre-se de que a pasta original é necessária para o 
     armazenamento dos arquivos temporários e não deve ser excluída.
6. O programa solicitará suas credenciais de login da Ubisoft. Quando você já tiver feito login, poderá optar por usar as credenciais salvas futuramente. Suas credenciais serão armazenadas localmente de forma segura.
7. Após fazer login, você verá as seguintes opções:
   - Adicionar jogadores: Insira as UIDs dos jogadores para adicionar à lista de jogadores a serem analisados. Os UIDs dos jogadores também serão salvos localmente para que você não precise inseri-los toda vez que iniciar o programa.
   - É necessário adicionar e selecionar pelo menos um jogador para ser analisado, mas você também pode selecionar um esquadrão de 5 jogadores ou até mais. Quando mais de um jogador é selecionado, o programa calculará médias ponderadas das estatísticas dos jogadores,
     fornecendo insights sobre o desempenho do esquadrão em diferentes mapas.
     Para encontrar o UID de um jogador:
     1. Acesse o [Site da Ubisoft R6 Stats](https://www.ubisoft.com/en-gb/game/rainbow-six/siege/stats/summary).
     2. Faça login com suas credenciais da Ubisoft.
     3. Após o login, o UID do jogador estará no final do link, após `summary/`.
   - Selecionar período de estatísticas: Escolha entre analisar estatísticas dos últimos 1, 2 ou 3 meses. Lembre-se de que a escolha do período de tempo afetará a precisão dos dados. 
     Um período de 3 meses fornece uma visão mais precisa do desempenho do jogador, enquanto períodos mais curtos podem variar mais devido à flutuação no tempo de jogo.

E pronto! ✅

Espero que isso ajude! Boa sorte e bom jogo! GL HF ✌️

## Exemplo de Uso

```
ESQUADRÃO: JOGADOR 1, JOGADOR 2, JOGADOR 3, JOGADOR 4, JOGADOR 5
INTERVALO DE DADOS: DATA - DATA (Período: X Meses)


PONTUAÇÕES DE DESEMPENHOS:
                LAIR : 22.78
          THEME PARK : 22.55
           COASTLINE : 21.90
              OREGON : 21.71
          CLUB HOUSE : 21.66
                BANK : 21.41
           CONSULATE : 21.27
              CHALET : 21.13
          SKYSCRAPER : 21.07
               VILLA : 20.76
     NIGHTHAVEN LABS : 20.59
             OUTBACK : 20.22
    KAFE DOSTOYEVSKY : 20.21
              BORDER : 20.21
               KANAL : 18.23
      EMERALD PLAINS : 4.28


TAXAS DE VITÓRIAS:
    KAFE DOSTOYEVSKY : 56.8%
          THEME PARK : 55.5%
          CLUB HOUSE : 54.3%
                LAIR : 54.1%
              OREGON : 53.6%
                BANK : 53.3%
           COASTLINE : 51.6%
               VILLA : 51.4%
              BORDER : 51.4%
      EMERALD PLAINS : 50.0%
           CONSULATE : 47.5%
              CHALET : 45.6%
          SKYSCRAPER : 40.3%
     NIGHTHAVEN LABS : 39.3%
             OUTBACK : 36.7%
               KANAL : 16.1%


ESTATÍSTICAS ADICIONAIS:
                LAIR : KD: 1.21, KOST: 66.6%
          THEME PARK : KD: 1.14, KOST: 65.9%
                BANK : KD: 1.14, KOST: 62.6%
              OREGON : KD: 1.13, KOST: 63.5%
          CLUB HOUSE : KD: 1.12, KOST: 63.3%
           COASTLINE : KD: 1.08, KOST: 64.1%
               VILLA : KD: 1.06, KOST: 60.7%
           CONSULATE : KD: 1.06, KOST: 62.3%
          SKYSCRAPER : KD: 1.04, KOST: 61.8%
              BORDER : KD: 1.03, KOST: 59.1%
     NIGHTHAVEN LABS : KD: 1.01, KOST: 60.4%
    KAFE DOSTOYEVSKY : KD: 1.00, KOST: 59%
              CHALET : KD: 0.99, KOST: 61.9%
             OUTBACK : KD: 0.99, KOST: 59.3%
      EMERALD PLAINS : KD: 0.91, KOST: 11.4%
               KANAL : KD: 0.78, KOST: 53.8%
```

## Direitos Autorais (c) 2021-2024 CNDRD
[Repositório da API](https://github.com/CNDRD/siegeapi)
[Documentação da API](https://cndrd.github.io/siegeapi)

## Aviso Importante
Esta ferramenta não é afiliada ou endossada pela Ubisoft ou pela equipe de desenvolvimento do Tom Clancy's Rainbow Six Siege. É um projeto independente criado para fins educacionais e analíticos.

## Contribuindo
Se você encontrar bugs ou tiver sugestões de melhorias, sinta-se à vontade para compartilhar. Este projeto é um trabalho em andamento e estou aberto a sugestões e correções para melhorá-lo.
