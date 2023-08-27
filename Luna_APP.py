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

        label_entrada = tk.Label(root, text="Digite sua mensagem:")
        label_entrada.pack()

        self.entrada_texto = tk.Entry(root, width=50)
        self.entrada_texto.pack()
        self.entrada_texto.focus_set()

        self.entrada_texto.bind("<Return>")

        botao_enviar = tk.Button(
            root, text="Enviar", command=self.obter_e_exibir_resposta
        )

        botao_enviar.pack()        
        self.botao_enviar = botao_enviar

        self.resposta_texto = tk.Text(root, width=50, height=10, state=tk.DISABLED)
        self.resposta_texto.pack()
        

        self.opcoes_avaliacao = ["Boa", "Ruim"] 
        self.avaliacao_var = tk.StringVar()
        self.radio_buttons = []
        self.entrada_usuario =  self.entrada_texto.get() 

        botao_feedback_boa = tk.Button(
            root, text="Boa", command=lambda: self.avaliar_resposta("Boa")
        )
        botao_feedback_boa.pack()

        botao_feedback_ruim = tk.Button(
            root, text="Ruim", command=lambda: self.avaliar_resposta("Ruim")
        )
        botao_feedback_ruim.pack()

    def avaliar_resposta(self, avaliacao):
        resposta = self.resposta_texto.get("1.0", tk.END)
        entrada_usuario = self.entrada_usuario 
        dialogo = f"Bot: {resposta}\nVocê: {entrada_usuario}"  # Concatenação do diálogo

        if avaliacao == "Boa":
            self.salvar_feedback_bom(dialogo)

        # Limpar a entrada e a resposta
        self.entrada_texto.delete(0, tk.END)
        self.resposta_texto.config(state=tk.NORMAL)
        self.resposta_texto.delete("1.0", tk.END)
        self.resposta_texto.config(state=tk.DISABLED)

            

    def exibir_interface_feedback(self):
        self.interface_feedback = tk.Toplevel(self.root)
        self.interface_feedback.title("Avaliar Resposta")        

        for opcao in self.opcoes_avaliacao:
            radio_button = tk.Radiobutton(
                self.interface_feedback, text=opcao, variable=self.avaliacao_var, value=opcao
            )
            radio_button.pack()
            self.radio_buttons.append(radio_button)

        botao_avaliar = tk.Button(
            self.interface_feedback,
            text="Enviar Avaliação",
            command=self.receber_avaliacao()
        )
        botao_avaliar.pack()

    def receber_avaliacao(self):
        avaliacao = self.avaliacao_var.get()
        
        dialogo = self.resposta_texto.get("1.0", tk.END)  # Obter a resposta exibida

        if avaliacao == "Boa":
            self.salvar_feedback_bom(dialogo)           
            

        self.interface_feedback.destroy()
        

    def obter_e_exibir_resposta(self, event=None):
        entrada_usuario = self.entrada_texto.get()
        resposta = self.chatbot.get_response(entrada_usuario)

        self.resposta_texto.config(state=tk.NORMAL)
        self.resposta_texto.delete("1.0", tk.END)
        self.resposta_texto.insert(tk.END, f"Você: {entrada_usuario}\n")
        self.resposta_texto.insert(tk.END, f"Bot: {resposta}\n\n")
        self.resposta_texto.config(state=tk.NORMAL)

        self.criar_audio_resposta(str(resposta))  # Criar e reproduzir áudio da resposta

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
