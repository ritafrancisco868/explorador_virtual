import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import json
import random
import math
import os
import webbrowser

def calcular_distancia(ponto1, ponto2):
    """Calcula a distância entre dois pontos em coordenadas geográficas (em km)."""
    lat1, lon1 = ponto1
    lat2, lon2 = ponto2
    raio_terra = 6371  # Raio médio da Terra em km

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    diff_lat = math.radians(lat2 - lat1)
    diff_lon = math.radians(lon2 - lon1)

    a = math.sin(diff_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(diff_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return raio_terra * c

def calcular_pontos(distancia_km):
    """Calcula os pontos com base na distância."""
    if distancia_km < 50:
        return 1000
    elif distancia_km < 500:
        return 800
    elif distancia_km < 2000:
        return 500
    elif distancia_km < 5000:
        return 200
    else:
        return 50

class ExploradorVirtual:
    def __init__(self):
        # Inicializar a janela principal
        self.janela = tk.Tk()
        self.janela.title("Explorador Virtual")
        self.janela.geometry("600x800")

        # Carregar dados dos países
        self.carregar_dados_paises()

        # Carregar/criar ficheiro de utilizadores
        self.carregar_utilizadores()

        # Variáveis de jogo
        self.pontos = 0
        self.paises_ja_mostrados = []
        self.pais_atual = None
        self.pistas_dadas = 0
        self.foto = None
        self.nivel_selecionado = None
        self.utilizador_atual = None
        self.tentativas_erradas = 0
        self.mapa_visivel = False
        self.vidas = 3  # Número de vidas (corações)

        # Dicionário de mapeamento de nomes de países para nomes de arquivos
        self.criar_mapeamento_imagens()

        # Mostrar página de login
        self.mostrar_login()

    def criar_mapeamento_imagens(self):
        """Cria um mapeamento entre nomes de países e nomes de arquivos de imagem."""
        # Verificar quais imagens existem na pasta
        pasta_imagens = "imagens"
        if os.path.exists(pasta_imagens):
            arquivos_existentes = os.listdir(pasta_imagens)
            print("\n=== IMAGENS DISPONÍVEIS NA PASTA ===")
            for arquivo in sorted(arquivos_existentes):
                print(f"  - {arquivo}")
            print("=" * 40)
        else:
            print(f"\n⚠️ AVISO: Pasta '{pasta_imagens}' não encontrada!")

    def normalizar_nome_arquivo(self, nome_pais):
        """
        Normaliza o nome do país para criar o nome do arquivo.
        Tenta várias variações para encontrar a imagem.
        """
        # Lista de possíveis variações do nome do arquivo
        variações = []
        
        # Versão 1: minúsculas, espaços para underscore, sem acentos
        nome_base = nome_pais.lower()
        nome_base = nome_base.replace(" ", "_")
        nome_base = nome_base.replace("-", "_")
        nome_base = nome_base.replace("'", "")
        nome_base = nome_base.replace("ã", "a").replace("á", "a").replace("à", "a").replace("â", "a")
        nome_base = nome_base.replace("é", "e").replace("ê", "e")
        nome_base = nome_base.replace("í", "i")
        nome_base = nome_base.replace("ó", "o").replace("ô", "o").replace("õ", "o")
        nome_base = nome_base.replace("ú", "u").replace("ü", "u")
        nome_base = nome_base.replace("ç", "c")
        
        variações.append(nome_base)
        
        # Versão 2: sem underscores (tudo junto)
        variações.append(nome_base.replace("_", ""))
        
        # Versão 3: com hífens em vez de underscores
        variações.append(nome_base.replace("_", "-"))
        
        # Versão 4: nome original com espaços
        variações.append(nome_pais.lower())
        
        # Versão 5: primeira palavra apenas (para "Estados Unidos" -> "estados")
        primeira_palavra = nome_base.split("_")[0]
        variações.append(primeira_palavra)
        
        return variações

    def carregar_imagem(self, nome_pais):
        """Carrega a imagem do país atual"""
        try:
            # Obter variações do nome do arquivo
            variações = self.normalizar_nome_arquivo(nome_pais)
            
            # Extensões possíveis
            extensões = [".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"]
            
            imagem_encontrada = False
            
            # Tentar cada variação com cada extensão
            for variação in variações:
                if imagem_encontrada:
                    break
                for ext in extensões:
                    caminho = f"imagens/{variação}{ext}"
                    if os.path.exists(caminho):
                        print(f"✓ Imagem encontrada: {caminho}")
                        imagem = Image.open(caminho)
                        imagem = imagem.resize((400, 250), Image.Resampling.LANCZOS)
                        self.foto = ImageTk.PhotoImage(imagem)
                        self.label_imagem.config(image=self.foto, text="")
                        imagem_encontrada = True
                        break
            
            if not imagem_encontrada:
                # Mostrar quais nomes foram tentados
                print(f"✗ Imagem não encontrada para '{nome_pais}'")
                print(f"  Tentativas: {', '.join([v + '.jpg' for v in variações])}")
                
                # Tentar carregar imagem padrão
                caminho_padrao = "imagens/padrao.jpg"
                if os.path.exists(caminho_padrao):
                    imagem_padrao = Image.open(caminho_padrao)
                    imagem_padrao = imagem_padrao.resize((400, 250), Image.Resampling.LANCZOS)
                    self.foto = ImageTk.PhotoImage(imagem_padrao)
                    self.label_imagem.config(image=self.foto, text="")
                    print(f"  → Usando imagem padrão")
                else:
                    # Mostrar texto se nem a imagem padrão existir
                    self.label_imagem.config(
                        text=f"[Imagem de {nome_pais} não disponível]\n\n💡 Dica: O arquivo deveria chamar-se:\n{variações[0]}.jpg",
                        font=("Arial", 10, "italic"),
                        fg="gray",
                        justify=tk.CENTER
                    )
                    print(f"  → Imagem padrão também não encontrada")
                    
        except Exception as e:
            # Em caso de qualquer erro, mostrar texto
            print(f"❌ Erro ao carregar imagem: {e}")
            self.label_imagem.config(
                text=f"[Erro ao carregar imagem de {nome_pais}]\n\n{str(e)}",
                font=("Arial", 10, "italic"),
                fg="red",
                justify=tk.CENTER
            )

    def carregar_utilizadores(self):
        """Carrega ou cria o ficheiro de utilizadores."""
        try:
            with open('utilizadores.json', 'r', encoding='utf-8') as f:
                self.utilizadores = json.load(f)
        except FileNotFoundError:
            # Criar ficheiro com utilizador padrão
            self.utilizadores = {
                "admin": {
                    "password": "admin123",
                    "pontuacao_maxima": 0,
                    "jogos_completos": 0
                }
            }
            self.guardar_utilizadores()

    def guardar_utilizadores(self):
        """Guarda os utilizadores no ficheiro."""
        with open('utilizadores.json', 'w', encoding='utf-8') as f:
            json.dump(self.utilizadores, f, indent=4, ensure_ascii=False)

    def mostrar_login(self):
        """Mostra a página de login."""
        # Limpar janela
        for widget in self.janela.winfo_children():
            widget.destroy()

        # Frame central
        frame_central = tk.Frame(self.janela, bg="#2C3E50")
        frame_central.pack(fill=tk.BOTH, expand=True)

        # Espaço superior
        tk.Label(frame_central, text="", bg="#2C3E50", height=3).pack()

        # Título
        tk.Label(
            frame_central,
            text="🌍 EXPLORADOR VIRTUAL 🌍",
            font=("Arial", 24, "bold"),
            bg="#2C3E50",
            fg="#ECF0F1"
        ).pack(pady=20)
        tk.Label(
            frame_central,
            text="Descobre países pelo mundo!",
            font=("Arial", 12, "italic"),
            bg="#2C3E50",
            fg="#BDC3C7"
        ).pack(pady=5)

        # Frame do formulário de login
        frame_login = tk.Frame(frame_central, bg="#34495E", padx=40, pady=30)
        frame_login.pack(pady=30)

        tk.Label(
            frame_login,
            text="BEM-VINDO!",
            font=("Arial", 18, "bold"),
            bg="#34495E",
            fg="#ECF0F1"
        ).pack(pady=15)

        # Username
        tk.Label(
            frame_login,
            text="Nome de utilizador:",
            font=("Arial", 11),
            bg="#34495E",
            fg="#ECF0F1"
        ).pack(pady=(10, 5))

        self.entrada_username = tk.Entry(frame_login, width=30, font=("Arial", 12))
        self.entrada_username.pack(pady=5)
        self.entrada_username.focus()

        # Password
        tk.Label(
            frame_login,
            text="Palavra-passe:",
            font=("Arial", 11),
            bg="#34495E",
            fg="#ECF0F1"
        ).pack(pady=(10, 5))

        self.entrada_password = tk.Entry(frame_login, width=30, font=("Arial", 12), show="*")
        self.entrada_password.pack(pady=5)

        # Bind Enter key
        self.entrada_username.bind('<Return>', lambda e: self.fazer_login())
        self.entrada_password.bind('<Return>', lambda e: self.fazer_login())

        # Label para mensagens de erro
        self.label_login_erro = tk.Label(
            frame_login,
            text="",
            font=("Arial", 10),
            bg="#34495E",
            fg="#E74C3C"
        )
        self.label_login_erro.pack(pady=5)

        # Botões
        frame_botoes = tk.Frame(frame_login, bg="#34495E")
        frame_botoes.pack(pady=15)

        tk.Button(
            frame_botoes,
            text="ENTRAR",
            command=self.fazer_login,
            font=("Arial", 12, "bold"),
            bg="#27AE60",
            fg="white",
            padx=20,
            pady=8,
            width=12
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            frame_botoes,
            text="REGISTAR",
            command=self.mostrar_registo,
            font=("Arial", 12, "bold"),
            bg="#3498DB",
            fg="white",
            padx=20,
            pady=8,
            width=12
        ).pack(side=tk.LEFT, padx=5)

        # Info na parte inferior
        tk.Label(
            frame_central,
            text="💡 Utilizador padrão: admin | Palavra-passe: admin123",
            font=("Arial", 9, "italic"),
            bg="#2C3E50",
            fg="#95A5A6"
        ).pack(side=tk.BOTTOM, pady=20)

    def fazer_login(self):
        """Processa o login do utilizador."""
        username = self.entrada_username.get().strip()
        password = self.entrada_password.get().strip()

        if not username or not password:
            self.label_login_erro.config(text="⚠️ Preencha todos os campos!")
            return

        if username in self.utilizadores:
            if self.utilizadores[username]["password"] == password:
                self.utilizador_atual = username
                self.label_login_erro.config(text="")
                self.mostrar_menu_nivel()
            else:
                self.label_login_erro.config(text="❌ Palavra-passe incorreta!")
                self.entrada_password.delete(0, tk.END)
        else:
            self.label_login_erro.config(text="❌ Utilizador não existe!")
            self.entrada_password.delete(0, tk.END)

    def mostrar_registo(self):
        """Mostra a página de registo de novo utilizador."""
        # Limpar janela
        for widget in self.janela.winfo_children():
            widget.destroy()

        # Frame central
        frame_central = tk.Frame(self.janela, bg="#2C3E50")
        frame_central.pack(fill=tk.BOTH, expand=True)

        # Espaço superior
        tk.Label(frame_central, text="", bg="#2C3E50", height=2).pack()

        # Título
        tk.Label(
            frame_central,
            text="📝 CRIAR CONTA",
            font=("Arial", 22, "bold"),
            bg="#2C3E50",
            fg="#ECF0F1"
        ).pack(pady=20)

        # Frame do formulário
        frame_registo = tk.Frame(frame_central, bg="#34495E", padx=40, pady=30)
        frame_registo.pack(pady=30)

        # Username
        tk.Label(
            frame_registo,
            text="Escolhe um nome de utilizador:",
            font=("Arial", 11),
            bg="#34495E",
            fg="#ECF0F1"
        ).pack(pady=(10, 5))

        self.entrada_novo_username = tk.Entry(frame_registo, width=30, font=("Arial", 12))
        self.entrada_novo_username.pack(pady=5)
        self.entrada_novo_username.focus()

        # Password
        tk.Label(
            frame_registo,
            text="Escolhe uma palavra-passe:",
            font=("Arial", 11),
            bg="#34495E",
            fg="#ECF0F1"
        ).pack(pady=(10, 5))

        self.entrada_nova_password = tk.Entry(frame_registo, width=30, font=("Arial", 12), show="*")
        self.entrada_nova_password.pack(pady=5)

        # Confirmar password
        tk.Label(
            frame_registo,
            text="Confirma a palavra-passe:",
            font=("Arial", 11),
            bg="#34495E",
            fg="#ECF0F1"
        ).pack(pady=(10, 5))

        self.entrada_confirmar_password = tk.Entry(frame_registo, width=30, font=("Arial", 12), show="*")
        self.entrada_confirmar_password.pack(pady=5)

        # Label para mensagens
        self.label_registo_msg = tk.Label(
            frame_registo,
            text="",
            font=("Arial", 10),
            bg="#34495E"
        )
        self.label_registo_msg.pack(pady=10)

        # Botões
        frame_botoes = tk.Frame(frame_registo, bg="#34495E")
        frame_botoes.pack(pady=15)

        tk.Button(
            frame_botoes,
            text="CRIAR CONTA",
            command=self.criar_conta,
            font=("Arial", 12, "bold"),
            bg="#27AE60",
            fg="white",
            padx=20,
            pady=8,
            width=12
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            frame_botoes,
            text="VOLTAR",
            command=self.mostrar_login,
            font=("Arial", 12, "bold"),
            bg="#95A5A6",
            fg="white",
            padx=20,
            pady=8,
            width=12
        ).pack(side=tk.LEFT, padx=5)

    def criar_conta(self):
        """Cria uma nova conta de utilizador."""
        username = self.entrada_novo_username.get().strip()
        password = self.entrada_nova_password.get().strip()
        confirmar = self.entrada_confirmar_password.get().strip()

        if not username or not password or not confirmar:
            self.label_registo_msg.config(text="⚠️ Preencha todos os campos!", fg="#E74C3C")
            return

        if len(username) < 3:
            self.label_registo_msg.config(text="⚠️ Nome deve ter pelo menos 3 caracteres!", fg="#E74C3C")
            return

        if len(password) < 4:
            self.label_registo_msg.config(text="⚠️ Palavra-passe deve ter pelo menos 4 caracteres!", fg="#E74C3C")
            return

        if password != confirmar:
            self.label_registo_msg.config(text="⚠️ As palavras-passe não coincidem!", fg="#E74C3C")
            self.entrada_confirmar_password.delete(0, tk.END)
            return

        if username in self.utilizadores:
            self.label_registo_msg.config(text="⚠️ Este utilizador já existe!", fg="#E74C3C")
            return

        # Criar novo utilizador
        self.utilizadores[username] = {
            "password": password,
            "pontuacao_maxima": 0,
            "jogos_completos": 0
        }
        self.guardar_utilizadores()

        self.label_registo_msg.config(text="✅ Conta criada com sucesso!", fg="#27AE60")
        self.janela.after(1500, self.mostrar_login)

    def normalizar_para_comparacao(self, nome):
        """Normaliza nome do país para comparação."""
        nome = nome.lower().strip()
        nome = nome.replace('á', 'a').replace('à', 'a').replace('â', 'a').replace('ã', 'a')
        nome = nome.replace('é', 'e').replace('ê', 'e')
        nome = nome.replace('í', 'i')
        nome = nome.replace('ó', 'o').replace('ô', 'o').replace('õ', 'o')
        nome = nome.replace('ú', 'u').replace('ü', 'u')
        nome = nome.replace('ç', 'c')
        return nome
    
    def encontrar_pais_no_json(self, nome_desejado):
        """Encontra o país no JSON mesmo com variações de nome."""
        nome_normalizado = self.normalizar_para_comparacao(nome_desejado)
        
        # Tentar correspondência exata primeiro
        if nome_desejado in self.paises:
            return nome_desejado
        
        # Tentar correspondência normalizada
        for pais_json in self.paises.keys():
            if self.normalizar_para_comparacao(pais_json) == nome_normalizado:
                return pais_json
        

    def carregar_dados_paises(self):
        """Carrega os dados dos países a partir do ficheiro JSON."""
        try:
            with open('paises.json', 'r', encoding='utf-8') as f:
                self.paises = json.load(f)

            # Lista de países para cada nível - TODOS os 20 países
            paises_faceis_desejados = [
                'Portugal', 'Espanha', 'França', 'Itália', 'Brasil',
                'Estados Unidos', 'Inglaterra', 'Alemanha', 'Japão', 'China',
                'Canadá', 'Austrália', 'México', 'Argentina', 'Rússia',
                'Índia', 'Coreia do Sul', 'Turquia', 'Egito', 'África do Sul'
            ]

            paises_medios_desejados = [
                'Grécia', 'Holanda', 'Suécia', 'Noruega', 'Polónia',
                'Irlanda', 'Áustria', 'Bélgica', 'Dinamarca', 'Finlândia',
                'Hungria', 'República Checa', 'Roménia', 'Bulgária', 'Suíça',
                'Nova Zelândia', 'Tailândia', 'Indonésia', 'Malásia', 'Filipinas',
                'Colômbia', 'Venezuela', 'Chile', 'Peru', 'Marrocos'
            ]

            # Encontrar países com busca inteligente
            facil_encontrados = []
            for pais_desejado in paises_faceis_desejados:
                pais_real = self.encontrar_pais_no_json(pais_desejado)
                if pais_real:
                    facil_encontrados.append(pais_real)
                else:
                    print(f"⚠️  País não encontrado: {pais_desejado}")
            
            medio_encontrados = []
            for pais_desejado in paises_medios_desejados:
                pais_real = self.encontrar_pais_no_json(pais_desejado)
                if pais_real:
                    medio_encontrados.append(pais_real)

            # Configurar níveis
            self.niveis = {
                'Fácil': facil_encontrados if facil_encontrados else list(self.paises.keys())[:20],
                'Médio': medio_encontrados if medio_encontrados else list(self.paises.keys())[20:45],
                'Difícil': []
            }

            # Países difíceis = todos os outros
            paises_faceis_medios = self.niveis['Fácil'] + self.niveis['Médio']
            self.niveis['Difícil'] = [p for p in self.paises.keys() if p not in paises_faceis_medios]

            # Se Difícil ficou vazio, usar todos
            if not self.niveis['Difícil']:
                self.niveis['Difícil'] = list(self.paises.keys())

            print(f"\n=== CONFIGURAÇÃO DOS NÍVEIS ===")
            print(f"Países Fácil ({len(self.niveis['Fácil'])}): {self.niveis['Fácil']}")
            print(f"Países Médio ({len(self.niveis['Médio'])}): {self.niveis['Médio']}")
            print(f"Países Difícil: {len(self.niveis['Difícil'])} países")
            print("=" * 50)

        except FileNotFoundError:
            messagebox.showerror("Erro", "Ficheiro 'paises.json' não encontrado!")
            self.janela.destroy()
        except json.JSONDecodeError:
            messagebox.showerror("Erro", "Ficheiro 'paises.json' está mal formatado!")
            self.janela.destroy()

    def mostrar_menu_nivel(self):
        """Mostra o menu de seleção de nível."""
        # Limpar janela
        for widget in self.janela.winfo_children():
            widget.destroy()

        # Frame com fundo colorido
        frame_principal = tk.Frame(self.janela, bg="#ECF0F1")
        frame_principal.pack(fill=tk.BOTH, expand=True)

        # Cabeçalho com info do utilizador
        frame_header = tk.Frame(frame_principal, bg="#3498DB", height=60)
        frame_header.pack(fill=tk.X)
        frame_header.pack_propagate(False)

        tk.Label(
            frame_header,
            text=f"👤 Bem-vindo, {self.utilizador_atual}!",
            font=("Arial", 12, "bold"),
            bg="#3498DB",
            fg="white"
        ).pack(side=tk.LEFT, padx=20, pady=15)

        stats = self.utilizadores[self.utilizador_atual]
        tk.Label(
            frame_header,
            text=f"🏆 Melhor: {stats['pontuacao_maxima']} pts | 🎮 Jogos: {stats['jogos_completos']}",
            font=("Arial", 10),
            bg="#3498DB",
            fg="white"
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            frame_header,
            text="Sair",
            command=self.mostrar_login,
            font=("Arial", 9),
            bg="#E74C3C",
            fg="white",
            padx=10,
            pady=5
        ).pack(side=tk.RIGHT, padx=20)

        # Título
        tk.Label(
            frame_principal,
            text="*** EXPLORADOR VIRTUAL ***",
            font=("Arial", 20, "bold"),
            bg="#ECF0F1"
        ).pack(pady=30)
        tk.Label(
            frame_principal,
            text="Escolhe o nível de dificuldade:",
            font=("Arial", 14),
            bg="#ECF0F1"
        ).pack(pady=10)

        # Frame para os botões
        frame_botoes = tk.Frame(frame_principal, bg="#ECF0F1")
        frame_botoes.pack(pady=20)

        # Botão Fácil
        tk.Button(
            frame_botoes,
            text=f"🌟 FÁCIL 🌟\n({len(self.niveis['Fácil'])} países conhecidos)",
            command=lambda: self.iniciar_jogo('Fácil'),
            font=("Arial", 14, "bold"),
            bg="#90EE90",
            fg="black",
            width=22,
            height=3,
            padx=10,
            pady=10
        ).pack(pady=10)

        # Botão Médio
        tk.Button(
            frame_botoes,
            text=f"⭐ MÉDIO ⭐\n({len(self.niveis['Médio'])} países com desafio)",
            command=lambda: self.iniciar_jogo('Médio'),
            font=("Arial", 14, "bold"),
            bg="#FFD700",
            fg="black",
            width=22,
            height=3,
            padx=10,
            pady=10
        ).pack(pady=10)

        # Botão Difícil
        tk.Button(
            frame_botoes,
            text=f"🔥 DIFÍCIL 🔥\n({len(self.niveis['Difícil'])} países)",
            command=lambda: self.iniciar_jogo('Difícil'),
            font=("Arial", 14, "bold"),
            bg="#FF6347",
            fg="white",
            width=22,
            height=3,
            padx=10,
            pady=10
        ).pack(pady=10)

    def iniciar_jogo(self, nivel):
        """Inicia o jogo com o nível selecionado."""
        self.nivel_selecionado = nivel
        self.pontos = 0
        self.paises_ja_mostrados = []
        self.tentativas_erradas = 0
        self.mapa_visivel = False
        self.vidas = 3  # Resetar vidas

        # Limpar janela e criar interface do jogo
        for widget in self.janela.winfo_children():
            widget.destroy()

        self.criar_interface()

    def criar_interface(self):
        """Cria a interface gráfica do jogo."""
        # Frame superior com título e info
        frame_topo = tk.Frame(self.janela)
        frame_topo.pack(pady=5)

        # Título
        tk.Label(
            frame_topo,
            text="*** EXPLORADOR VIRTUAL ***",
            font=("Arial", 16, "bold")
        ).pack()

        # Nível, pontuação e vidas na mesma linha
        frame_info = tk.Frame(frame_topo)
        frame_info.pack()

        tk.Label(
            frame_info,
            text=f"👤 {self.utilizador_atual}",
            font=("Arial", 10, "bold"),
            fg="purple"
        ).pack(side=tk.LEFT, padx=10)

        tk.Label(
            frame_info,
            text=f"Nível: {self.nivel_selecionado}",
            font=("Arial", 11, "bold"),
            fg="blue"
        ).pack(side=tk.LEFT, padx=10)

        self.label_pontos = tk.Label(
            frame_info,
            text=f"Pontos: {self.pontos}",
            font=("Arial", 11, "bold"),
            fg="green"
        )
        self.label_pontos.pack(side=tk.LEFT, padx=10)

        # Frame para os corações (vidas)
        self.frame_vidas = tk.Frame(frame_info)
        self.frame_vidas.pack(side=tk.LEFT, padx=10)

        # Atualizar corações
        self.atualizar_vidas()

        # Botão para voltar ao menu
        tk.Button(
            frame_info,
            text="↩ Menu",
            command=self.voltar_menu,
            font=("Arial", 9),
            bg="gray",
            fg="white",
            padx=5,
            pady=2
        ).pack(side=tk.LEFT, padx=10)

        # Frame para a imagem
        self.frame_imagem = tk.Frame(self.janela, width=400, height=250)
        self.frame_imagem.pack(pady=5)
        self.frame_imagem.pack_propagate(False)

        self.label_imagem = tk.Label(self.frame_imagem, text="Carregando...")
        self.label_imagem.pack()

        # Labels para pistas
        self.label_pista1 = tk.Label(self.janela, text="", font=("Arial", 10))
        self.label_pista1.pack(pady=2)

        self.label_pista2 = tk.Label(self.janela, text="", font=("Arial", 10))
        self.label_pista2.pack(pady=2)

        self.label_pista3 = tk.Label(self.janela, text="", font=("Arial", 10))
        self.label_pista3.pack(pady=2)

        # Botão para mostrar/esconder o mapa-mundi
        self.botao_mapa_mundi = tk.Button(
            self.janela,
            text="🗺️ Ver Mapa-Mundi",
            command=self.toggle_mapa_mundi,
            font=("Arial", 10, "bold"),
            bg="#3498DB",
            fg="white",
            padx=10,
            pady=5,
            state=tk.NORMAL
        )
        self.botao_mapa_mundi.pack(pady=5)

        # Botão para ampliar o mapa
        self.botao_ampliar_mapa = tk.Button(
            self.janela,
            text="🔍 Ampliar Mapa",
            command=self.ampliar_mapa,
            font=("Arial", 10, "bold"),
            bg="#27AE60",
            fg="white",
            padx=10,
            pady=5,
            state=tk.DISABLED  # Começa desativado
        )
        self.botao_ampliar_mapa.pack(pady=5)

        # Entrada para o nome do país
        tk.Label(
            self.janela,
            text="Escreve o nome do país:",
            font=("Arial", 10)
        ).pack(pady=5)

        self.entrada = tk.Entry(self.janela, width=30, font=("Arial", 11))
        self.entrada.pack(pady=5)
        self.entrada.bind('<Return>', lambda e: self.verificar())

        # Botão para verificar a resposta
        self.botao_verificar = tk.Button(
            self.janela,
            text="VERIFICAR",
            command=self.verificar,
            font=("Arial", 11, "bold"),
            bg="blue",
            fg="white",
            padx=20,
            pady=5
        )
        self.botao_verificar.pack(pady=5)

        # Label para mostrar o resultado
        self.label_resultado = tk.Label(
            self.janela,
            text="",
            font=("Arial", 10, "bold"),
            height=3
        )
        self.label_resultado.pack(pady=5)

        # Frame para o botão próximo
        self.frame_botao_proximo = tk.Frame(self.janela)
        self.frame_botao_proximo.pack(pady=5)

        # Botão para passar ao próximo país
        self.botao_proximo = tk.Button(
            self.frame_botao_proximo,
            text="PRÓXIMO PAÍS >>",
            command=self.proxima_ronda,
            font=("Arial", 10, "bold"),
            bg="green",
            fg="white",
            padx=10,
            pady=8
        )

        # Iniciar a primeira ronda
        self.nova_ronda()

    def atualizar_vidas(self):
        """Atualiza a exibição dos corações (vidas)."""
        # Limpar corações atuais
        for widget in self.frame_vidas.winfo_children():
            widget.destroy()

        # Adicionar corações com base nas vidas restantes
        for i in range(self.vidas):
            tk.Label(
                self.frame_vidas,
                text="❤️",
                font=("Arial", 12),
                fg="red"
            ).pack(side=tk.LEFT)

        for i in range(3 - self.vidas):
            tk.Label(
                self.frame_vidas,
                text="💔",
                font=("Arial", 12),
                fg="gray"
            ).pack(side=tk.LEFT)

    def voltar_menu(self):
        """Volta ao menu e atualiza estatísticas."""
        if self.pontos > self.utilizadores[self.utilizador_atual]["pontuacao_maxima"]:
            self.utilizadores[self.utilizador_atual]["pontuacao_maxima"] = self.pontos
            self.guardar_utilizadores()

        self.mostrar_menu_nivel()

    def toggle_mapa_mundi(self):
        """Mostra ou esconde o mapa-mundi."""
        if self.mapa_visivel:
            # Se o mapa estiver visível, esconde-o e mostra a imagem do país
            self.carregar_imagem(self.pais_atual)
            self.botao_ampliar_mapa.config(state=tk.DISABLED)
            self.mapa_visivel = False
            self.botao_mapa_mundi.config(text="🗺️ Ver Mapa-Mundi")
        else:
            # Se o mapa não estiver visível, mostra-o
            self.mostrar_mapa_mundi()
            self.botao_ampliar_mapa.config(state=tk.NORMAL)
            self.mapa_visivel = True
            self.botao_mapa_mundi.config(text="🗺️ Esconder Mapa")

    def mostrar_mapa_mundi(self):
        """Mostra a imagem estática do mapa-mundi."""
        try:
            caminho = "imagens/mapa_mundo.jpg"
            if os.path.exists(caminho):
                imagem = Image.open(caminho)
                imagem = imagem.resize((400, 250), Image.Resampling.LANCZOS)
                self.foto = ImageTk.PhotoImage(imagem)
                self.label_imagem.config(image=self.foto, text="")
            else:
                self.label_imagem.config(
                    text="[Imagem 'mapa_mundo.jpg' não encontrada]",
                    font=("Arial", 12, "italic"),
                    fg="red"
                )
        except Exception as e:
            print(f"Erro ao carregar mapa-mundi: {e}")
            self.label_imagem.config(
                text=f"[Erro ao carregar mapa-mundi: {e}]",
                font=("Arial", 10, "italic"),
                fg="red"
            )

    def ampliar_mapa(self):
        """Abre o mapa-mundi numa janela maior."""
        try:
            caminho = "imagens/mapa_mundo.jpg"
            if os.path.exists(caminho):
                imagem = Image.open(caminho)

                # Criar uma nova janela para mostrar o mapa ampliado
                janela_mapa = tk.Toplevel(self.janela)
                janela_mapa.title("Mapa-Mundi Ampliado")

                # Ajustar o tamanho da janela
                largura, altura = imagem.size
                nova_largura = 800
                nova_altura = int(altura * (nova_largura / largura))
                imagem = imagem.resize((nova_largura, nova_altura), Image.Resampling.LANCZOS)

                foto_ampliada = ImageTk.PhotoImage(imagem)

                label_mapa_ampliado = tk.Label(janela_mapa, image=foto_ampliada)
                label_mapa_ampliado.image = foto_ampliada  # Manter uma referência
                label_mapa_ampliado.pack()

                # Botão para fechar a janela ampliada
                tk.Button(
                    janela_mapa,
                    text="Fechar",
                    command=janela_mapa.destroy,
                    font=("Arial", 10, "bold"),
                    bg="#E74C3C",
                    fg="white",
                    padx=10,
                    pady=5
                ).pack(pady=10)
            else:
                messagebox.showerror("Erro", "Imagem 'mapa_mundo.jpg' não encontrada!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ampliar mapa: {e}")

    def abrir_localizacao_no_mapa(self):
        """Abre o Google Maps com a localização exata do país atual."""
        if self.vidas <= 0:
            messagebox.showwarning("Sem Vidas", "Não tens mais vidas para usar a localização exata!")
            self.game_over()
            return

        if self.pais_atual and self.pais_atual in self.paises:
            lat, lon = self.paises[self.pais_atual]["coordenadas"]
            url = f"https://www.google.com/maps?q={lat},{lon}"
            webbrowser.open(url)

            # Reduzir uma vida
            self.vidas -= 1
            self.atualizar_vidas()

            if self.vidas <= 0:
                messagebox.showwarning("Sem Vidas", "Perdeu todas as vidas! Game Over!")
                self.game_over()
        else:
            messagebox.showwarning("Aviso", "Não há um país selecionado para mostrar no mapa.")

    def game_over(self):
        """Termina o jogo e mostra mensagem de Game Over."""
        messagebox.showinfo("Game Over", f"Game Over! Pontuação final: {self.pontos}")
        self.voltar_menu()

    def nova_ronda(self):
        """Inicia uma nova ronda do jogo."""
        # Selecionar país do nível escolhido
        paises_nivel = self.niveis[self.nivel_selecionado]

        # Remover países já mostrados
        paises_disponiveis = [p for p in paises_nivel if p not in self.paises_ja_mostrados and p in self.paises]

        # Se já mostrámos todos os países do nível, mostrar mensagem e voltar ao menu
        if not paises_disponiveis:
            messagebox.showinfo("Fim do nível", f"Parabéns! Completaste o nível {self.nivel_selecionado}!")
            self.voltar_menu()
            return

        # Escolher país aleatório
        self.pais_atual = random.choice(paises_disponiveis)
        self.paises_ja_mostrados.append(self.pais_atual)

        print(f"\n=== NOVA RONDA ===")
        print(f"País escolhido: {self.pais_atual}")
        print(f"Países já mostrados: {len(self.paises_ja_mostrados)}/{len(paises_nivel)}")

        info = self.paises[self.pais_atual]

        # Carregar imagem
        self.carregar_imagem(self.pais_atual)

        # Resetar pistas
        self.pistas_dadas = 0

        # Mostrar a primeira pista
        self.label_pista1.config(text=f"PISTA 1: Continente - {info['continente']}")
        self.label_pista2.config(text="")
        self.label_pista3.config(text="")

        # Limpar campos
        self.entrada.delete(0, tk.END)
        self.entrada.config(state='normal')
        self.botao_verificar.config(state='normal')
        self.label_resultado.config(text="")

        # Esconder botão próximo
        self.botao_proximo.pack_forget()

        # Resetar contagem de tentativas erradas
        self.tentativas_erradas = 0
        self.mapa_visivel = False
        self.botao_mapa_mundi.config(text="🗺️ Ver Mapa-Mundi")
        self.botao_ampliar_mapa.config(state=tk.DISABLED)

        self.entrada.focus()

    def mostrar_pista_extra(self):
        """Mostra pistas adicionais quando o jogador erra."""
        info = self.paises[self.pais_atual]

        if self.pistas_dadas == 0:
            self.label_pista2.config(text=f"PISTA 2: Clima - {info['clima']}")
            self.pistas_dadas = 1
        elif self.pistas_dadas == 1 and 'animais' in info and len(info['animais']) > 0:
            self.label_pista3.config(text=f"PISTA 3: Animal - {info['animais'][0]}")
            self.pistas_dadas = 2

    def normalizar_nome_pais(self, nome):
        """Normaliza o nome do país para comparação (remove acentos, converte case)."""
        nome = nome.strip().lower()
        # Remover acentos
        nome = nome.replace('á', 'a').replace('à', 'a').replace('â', 'a').replace('ã', 'a')
        nome = nome.replace('é', 'e').replace('ê', 'e')
        nome = nome.replace('í', 'i')
        nome = nome.replace('ó', 'o').replace('ô', 'o').replace('õ', 'o')
        nome = nome.replace('ú', 'u').replace('ü', 'u')
        nome = nome.replace('ç', 'c')
        return nome
    
    def encontrar_pais_por_nome(self, palpite):
        """Encontra o país no dicionário considerando variações do nome."""
        palpite_normalizado = self.normalizar_nome_pais(palpite)
        
        # Verificar correspondência exata primeiro
        for pais in self.paises.keys():
            if self.normalizar_nome_pais(pais) == palpite_normalizado:
                return pais
        
        # Se não encontrar, retornar None
        return None

    def verificar(self):
        """Verifica a resposta do jogador."""
        palpite_original = self.entrada.get().strip()

        if not palpite_original:
            return
        
        # Formatar o palpite (Title Case)
        palpite = palpite_original.title()
        
        # Encontrar o país correspondente
        pais_encontrado = self.encontrar_pais_por_nome(palpite)

        if pais_encontrado and pais_encontrado == self.pais_atual:
            # Resposta correta
            self.pontos += 1000
            self.label_pontos.config(text=f"Pontos: {self.pontos}")

            info = self.paises[self.pais_atual]
            self.label_resultado.config(
                text=f"*** CORRETO! ***\nEra {self.pais_atual}!\nCapital: {info['capital']}",
                fg="green"
            )

            # Desativar campos
            self.entrada.config(state='disabled')
            self.botao_verificar.config(state='disabled')

            # Mostrar botão "Próximo País"
            self.botao_proximo.pack()

            # Incrementar jogos completos
            self.utilizadores[self.utilizador_atual]["jogos_completos"] += 1
            self.guardar_utilizadores()

            # Resetar contagem de tentativas erradas
            self.tentativas_erradas = 0

        elif pais_encontrado:
            # País válido, mas errado
            coord1 = tuple(self.paises[pais_encontrado]['coordenadas'])
            coord2 = tuple(self.paises[self.pais_atual]['coordenadas'])
            dist = calcular_distancia(coord1, coord2)
            pts = calcular_pontos(dist)
            self.pontos += pts

            self.label_pontos.config(text=f"Pontos: {self.pontos}")
            self.label_resultado.config(
                text=f"Não é {pais_encontrado}!\nDistância: {dist:.0f} km\n(+{pts} pontos)",
                fg="red"
            )

            # Incrementar contagem de tentativas erradas
            self.tentativas_erradas += 1

            # Se errar 10 vezes, abrir o mapa com a localização exata
            if self.tentativas_erradas >= 10:
                self.abrir_localizacao_no_mapa()
                self.label_resultado.config(
                    text=f"Não é {pais_encontrado}!\nDistância: {dist:.0f} km\n(+{pts} pontos)\n🗺️ A localização exata foi aberta no navegador!",
                    fg="red"
                )
                self.tentativas_erradas = 0  # Resetar contagem

            # Mostrar pista extra
            self.mostrar_pista_extra()

            self.entrada.delete(0, tk.END)
            self.entrada.focus()

        else:
            # País não existe
            self.label_resultado.config(
                text=f"'{palpite}' não está na lista!\n💡 Dica: Verifica a ortografia",
                fg="orange"
            )
            self.entrada.delete(0, tk.END)
            self.entrada.focus()

    def proxima_ronda(self):
        """Passa para a próxima ronda do jogo."""
        self.nova_ronda()

    def iniciar(self):
        """Inicia a aplicação."""
        self.janela.mainloop()

if __name__ == "__main__":
    jogo = ExploradorVirtual()
    jogo.iniciar()