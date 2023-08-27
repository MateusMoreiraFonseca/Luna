import tkinter as tk
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from gtts import gTTS
import os
import pygame


class InterfaceChatbot:
    def __init__(self, root, chatbot):
        self.root = root
        self.root.title("Interface do Chatbot")
        self.chatbot = chatbot
        self.should_restart = False

        label_entrada = tk.Label(root, text="Digite sua mensagem:")
        label_entrada.pack()

        self.entrada_texto = tk.Entry(root, width=50)
        self.entrada_texto.pack()
        self.entrada_texto.focus_set()

        self.entrada_texto.bind("<Return>", self.obter_e_exibir_resposta)

        botao_enviar = tk.Button(
            root, text="Enviar", command=self.obter_e_exibir_resposta
        )
        botao_enviar.pack()
        self.botao_enviar = botao_enviar

        self.resposta_texto = tk.Text(root, width=50, height=10, state=tk.NORMAL)
        self.resposta_texto.pack()

        self.opcoes_avaliacao = ["Boa", "Ruim"]
        self.avaliacao_var = tk.StringVar()
        self.radio_buttons = []

        botao_feedback_boa = tk.Button(
            root, text="Boa", command=lambda: self.avaliar_resposta("Boa"), width=10
        )
        botao_feedback_boa.pack(side="left", padx=5, pady=2)

        botao_feedback_ruim = tk.Button(
            root, text="Ruim", command=lambda: self.avaliar_resposta("Ruim"), width=10
        )
        botao_feedback_ruim.pack(side="left", padx=5, pady=2)

        botao_treinar = tk.Button(
            root,
            text="Treinar Luna com Feedbacks",
            command=self.fechar_e_reiniciar,
            width=25,
        )
        botao_treinar.pack(side="right", padx=5, pady=2)

        botao_sair = tk.Button(root, text="Sair", command=self.sair, width=10)
        botao_sair.pack(side="right", padx=5, pady=2)

    def sair(self):
        self.should_restart = False  # Defina should_restart como False
        self.root.destroy()  # Feche a janela

    def fechar_e_reiniciar(self):
        self.should_restart = True
        self.root.destroy()

    def avaliar_resposta(self, avaliacao):
        resposta = self.resposta_texto.get("1.0", tk.END)
        dialogo = f"{resposta}"

        if avaliacao == "Boa":
            self.salvar_feedback_bom(dialogo)

        self.entrada_texto.delete(0, tk.END)
        self.resposta_texto.config(state=tk.NORMAL)
        self.resposta_texto.delete("1.0", tk.END)
        self.resposta_texto.config(state=tk.NORMAL)

    def obter_e_exibir_resposta(self, event=None):
        entrada_usuario = self.entrada_texto.get()
        self.entrada_usuario = entrada_usuario
        resposta = self.chatbot.get_response(entrada_usuario)

        self.resposta_texto.config(state=tk.NORMAL)
        self.resposta_texto.delete("1.0", tk.END)
        self.resposta_texto.insert(tk.END, f"Você: {entrada_usuario}\n")
        self.resposta_texto.insert(tk.END, f"Bot: {resposta}\n\n")
        self.resposta_texto.config(state=tk.DISABLED)

        self.criar_audio_resposta(str(resposta))
        self.entrada_texto.delete(0, tk.END)

    def criar_audio_resposta(self, texto):
        tts = gTTS(texto, lang="pt-BR")
        tts.save("resposta.mp3")

        pygame.mixer.init()
        pygame.mixer.music.load("resposta.mp3")
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.quit()
        os.remove("resposta.mp3")

    def salvar_feedback_bom(self, dialogo):
        with open("feedback_bom.txt", "a", encoding="utf-8") as f:
            f.write(f"{dialogo}\n\n")


def treinar_chatbot(chatbot):
    feedbacks = []
    if os.path.exists("feedback_bom.txt"):
        with open("feedback_bom.txt", "r", encoding="utf-8") as f:
            feedbacks = f.read().split("\n\n")

    if feedbacks:
        treinador = ChatterBotCorpusTrainer(chatbot)
        treinador.train("chatterbot.corpus.portuguese")


if __name__ == "__main__":
    while True:
        root = tk.Tk()
        chatbot = ChatBot("Luna- Assitente de Voz")
        treinar_chatbot(chatbot)
        app = InterfaceChatbot(root, chatbot)
        root.protocol(
            "WM_DELETE_WINDOW", app.sair
        )  # Configura o método "sair" para quando a janela for fechada
        root.mainloop()

        if hasattr(app, "should_restart") and app.should_restart:
            print("Reiniciado com sucesso!")
        else:
            break
