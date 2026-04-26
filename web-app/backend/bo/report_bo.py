import asyncio
import json
import os
import subprocess
import tempfile
from datetime import datetime

from fpdf import FPDF

from dao.client_dao import ClientDAO
from vo.client_vo import ClientVO
from vo.report_vo import ReportResultVO


RIVET_RUNNER_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "rivet-runner")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "output")


class ReportBO:
    def __init__(self, client_dao: ClientDAO):
        self.client_dao = client_dao

    async def generate_reports(self, client_ids: list[str]) -> list[ReportResultVO]:
        tasks = [self._generate_single(cid) for cid in client_ids]
        return await asyncio.gather(*tasks)

    async def _generate_single(self, client_id: str) -> ReportResultVO:
        try:
            client = self.client_dao.get_client(client_id)
            print(f"[BO] Generating report for: {client.name}")

            files = self.client_dao.get_client_files(client_id)
            print(f"[DAO] Files loaded for {client_id}: {list(files.keys())}")

            print(f"[Rivet] Running graph for {client.name}...")
            letter_text = await self._run_rivet(files)
            print(f"[Rivet] Letter generated ({len(letter_text)} chars)")

            filename = self._export_pdf(letter_text, client)
            print(f"[pdf] File saved: {filename}")

            return ReportResultVO(
                client_id=client_id,
                client_name=client.name,
                status="success",
                filename=filename,
                letter_text=letter_text,
            )
        except Exception as exc:
            print(f"[ERROR] Failed for {client_id}: {exc}")
            return ReportResultVO(
                client_id=client_id,
                client_name=client_id,
                status="error",
                error=str(exc),
            )

    async def _run_rivet(self, file_contents: dict[str, str]) -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._run_rivet_sync, file_contents)

    def _run_rivet_sync(self, file_contents: dict[str, str]) -> str:
        # Write inputs to a temp file to avoid Windows command-line length limit (~8000 chars)
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as tmp:
            json.dump(file_contents, tmp)
            tmp_path = tmp.name

        with tempfile.NamedTemporaryFile(
            suffix=".txt", delete=False, encoding="utf-8", mode="w"
        ) as out_tmp:
            out_path = out_tmp.name

        try:
            result = subprocess.run(
                ["node", "run_graph.js", tmp_path, out_path],
                cwd=os.path.abspath(RIVET_RUNNER_DIR),
                capture_output=True,
                encoding="utf-8",
                env={**os.environ},
                timeout=120,
            )
        finally:
            os.unlink(tmp_path)

        if result.returncode != 0:
            os.unlink(out_path)
            raise RuntimeError(result.stderr)

        with open(out_path, encoding="utf-8") as f:
            letter = f.read().strip()
        os.unlink(out_path)

        if not letter:
            raise RuntimeError(f"Rivet returned no text. stderr: {result.stderr}")
        return letter

    @staticmethod
    def _safe(text: str) -> str:
        """Replace typographic Unicode chars with Latin-1 safe equivalents."""
        return (
            text
            .replace("—", "-")
            .replace("–", "-")
            .replace("“", '"')
            .replace("”", '"')
            .replace("‘", "'")
            .replace("’", "'")
            .replace("…", "...")
            .replace("•", "-")
            .replace("·", "*")
            .encode("latin-1", errors="replace").decode("latin-1")
        )

    def _export_pdf(self, letter_text: str, client: ClientVO) -> str:
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        advisor_name = self._safe(client.advisor_name)
        client_email = self._safe(client.email)

        class XPReport(FPDF):
            def header(self):
                self.set_font("Helvetica", "I", 9)
                self.set_text_color(140, 140, 140)
                self.cell(0, 8, "XP Investimentos | Relatorio Mensal de Investimentos", align="C")
                self.ln(3)

            def footer(self):
                self.set_y(-14)
                self.set_font("Helvetica", "I", 9)
                self.set_text_color(140, 140, 140)
                self.cell(
                    0, 10,
                    f"Assessor: {advisor_name}  |  {client_email}  |  XP Investimentos - Confidencial",
                    align="C",
                )

        pdf = XPReport(orientation="P", unit="mm", format="A4")
        pdf.set_margins(25, 22, 25)
        pdf.set_auto_page_break(auto=True, margin=18)
        pdf.add_page()

        # Title
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(16, 63, 108)
        pdf.cell(0, 10, self._safe(f"Relatorio Mensal - {client.name}"), align="C")
        pdf.ln(7)

        # Date
        date_str = datetime.now().strftime("%B de %Y")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(110, 110, 110)
        pdf.cell(0, 6, date_str, align="C")
        pdf.ln(10)

        # Body
        pdf.set_text_color(30, 30, 30)
        pdf.set_font("Helvetica", "", 11)
        for block in letter_text.split("\n\n"):
            block = block.strip()
            if not block:
                continue
            pdf.multi_cell(0, 6, self._safe(block))
            pdf.ln(4)

        filename = f"relatorio_{client.id}_{datetime.now().strftime('%Y%m')}.pdf"
        filepath = os.path.join(OUTPUT_DIR, filename)
        pdf.output(filepath)
        return filename