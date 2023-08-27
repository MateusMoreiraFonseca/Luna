import tkinter as tk
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from gtts import gTTS
import joblib
import os

import pygame


class InterfaceChatbot:
    def __init__(self, root, chatbot):
        self.root = root
        self.root.title("Interface do Chatbot")
        self.chatbot = chatbot

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

        self.resposta_texto = tk.Text(root, width=50, height=10, state=tk.DISABLED)
        self.resposta_texto.pack()

        botao_feedback = tk.Button(
            root, text="Avaliar Resposta", command=self.exibir_interface_feedback
        )
        botao_feedback.pack()

        self.avaliacao_var = tk.StringVar()
        self.radio_buttons = []

    def obter_e_exibir_resposta(self, event=None):
        entrada_usuario = self.entrada_texto.get()
        resposta = self.chatbot.get_response(entrada_usuario)

        self.resposta_texto.config(state=tk.NORMAL)
        self.resposta_texto.delete("1.0", tk.END)
        self.resposta_texto.insert(tk.END, str(resposta))
        self.resposta_texto.config(state=tk.NORMAL)

        self.criar_audio_resposta(str(resposta))  # Criar e reproduzir áudio da resposta

        self.entrada_texto.delete(0, tk.END)

        self.salvar_feedback_bom(entrada_usuario, str(resposta))

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

    def salvar_feedback_bom(self, entrada, resposta):
        with open("feedback_bom.txt", "a", encoding="utf-8") as f:
            f.write(f"Entrada: {entrada}\nResposta: {resposta}\n\n")

    def exibir_interface_feedback(self, resposta):
        self.interface_feedback = tk.Toplevel(self.root)
        self.interface_feedback.title("Avaliar Resposta")

        self.avaliacao_var.set("Boa")

        opcoes_avaliacao = ["Boa", "Ruim"]
        for opcao in opcoes_avaliacao:
            radio_button = tk.Radiobutton(
                self.interface_feedback, text=opcao, variable=self.avaliacao_var, value=opcao
            )
            radio_button.pack()
            self.radio_buttons.append(radio_button)

        botao_avaliar = tk.Button(
            self.interface_feedback,
            text="Enviar Avaliação",
            command=lambda: self.receber_avaliacao(resposta),
        )
        botao_avaliar.pack()


    def receber_avaliacao(self, resposta):
        avaliacao = self.avaliacao_var.get()
        if avaliacao == "Boa":
            entrada_usuario = self.entrada_texto.get()
            self.salvar_feedback_bom(entrada_usuario, resposta)

        self.interface_feedback.destroy()
        self.avaliacao_var.set("Boa")


def treinar_chatbot():
    chatbot = ChatBot("MeuChatBot")

    # Verifica se o arquivo de feedback bom existe
    if not os.path.exists("feedback_bom.txt"):
        treinador = ChatterBotCorpusTrainer(chatbot)
        treinador.train("chatterbot.corpus.portuguese")

    return chatbot


if __name__ == "__main__":
    chatbot = treinar_chatbot()

    root = tk.Tk()
    app = InterfaceChatbot(root, chatbot)
    root.mainloop()
