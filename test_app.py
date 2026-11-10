
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app as patentflow
from werkzeug.security import generate_password_hash


class TestPatentFlow(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.banco_teste = Path(self.temp.name) / "teste.sqlite3"

        # Substitui o banco real por um banco temporário.
        self.patch_db = patch.object(patentflow, "DB", self.banco_teste)
        self.patch_db.start()

        patentflow.app.config.update(TESTING=True)
        patentflow.init_db()
        self.client = patentflow.app.test_client()

        with patentflow.app.app_context():
            conexao = patentflow.db()
            conexao.execute(
                "INSERT INTO usuario(nome, senha_hash) VALUES (?, ?)",
                ("admin_teste", generate_password_hash("senha_segura_123"))
            )
            conexao.commit()

    def tearDown(self):
        self.patch_db.stop()
        self.temp.cleanup()

    def token_csrf(self):
        with self.client.session_transaction() as sessao:
            sessao["csrf"] = "token_de_teste"
        return "token_de_teste"

    def fazer_login(self):
        token = self.token_csrf()
        return self.client.post("/login", data={
            "nome": "admin_teste",
            "senha": "senha_segura_123",
            "csrf_token": token
        })

    def test_acesso_sem_login(self):
        resposta = self.client.get("/")
        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/login", resposta.headers["Location"])

    def test_login_valido(self):
        resposta = self.fazer_login()
        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(resposta.headers["Location"], "/")

    def test_cadastro_patente(self):
        self.fazer_login()
        token = self.token_csrf()

        resposta = self.client.post("/patentes/nova", data={
            "numero_processo": "TESTE-001",
            "inventor": "Ana Silva",
            "instituto": "Instituto de Biologia",
            "data_registro": "2026-11-16",
            "status": "Em andamento",
            "custos": "150",
            "csrf_token": token
        })

        self.assertEqual(resposta.status_code, 302)

        with patentflow.app.app_context():
            patente = patentflow.db().execute(
                "SELECT * FROM patente WHERE numero_processo = ?",
                ("TESTE-001",)
            ).fetchone()

            self.assertIsNotNone(patente)
            self.assertEqual(patente["inventor"], "Ana Silva")


    def test_cadastro_sem_csrf(self):
        self.fazer_login()

        resposta = self.client.post("/patentes/nova", data={
            "numero_processo": "TESTE-002",
            "inventor": "Ana Silva",
            "instituto": "Instituto de Biologia",
            "data_registro": "2026-11-16",
            "status": "Em andamento",
            "custos": "150"
        })

        self.assertEqual(resposta.status_code, 400)

        with patentflow.app.app_context():
            patente = patentflow.db().execute(
                "SELECT * FROM patente WHERE numero_processo = ?",
                ("TESTE-002",)
            ).fetchone()

            self.assertIsNone(patente)




    def test_cadastro_custos_invalidos(self):
        self.fazer_login()
        token = self.token_csrf()

        for valor in ["NaN", "Infinity", "-10"]:
            with self.subTest(custos=valor):
                resposta = self.client.post("/patentes/nova", data={
                    "numero_processo": "TESTE-INVALIDO",
                    "inventor": "Ana Silva",
                    "instituto": "Instituto de Biologia",
                    "data_registro": "2026-11-10",
                    "status": "Em andamento",
                    "custos": valor,
                    "csrf_token": token
                })

                self.assertEqual(resposta.status_code, 200)

                with patentflow.app.app_context():
                    patente = patentflow.db().execute(
                        "SELECT * FROM patente WHERE numero_processo = ?",
                        ("TESTE-INVALIDO",)
                    ).fetchone()

                    self.assertIsNone(patente)

if __name__ == "__main__":
    unittest.main()
