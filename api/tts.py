from http.server import BaseHTTPRequestHandler
import asyncio
import edge_tts
import tempfile
import io

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse query parameters
        from urllib.parse import urlparse, parse_qs
        query = parse_qs(urlparse(self.path).query)
        text = query.get('text', [''])[0]
        voice = query.get('voice', ['en-US-AriaNeural'])[0]

        if not text:
            self.send_response(400)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Missing "text" parameter')
            return

        # Generate TTS
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio_data = loop.run_until_complete(self._generate_tts(text, voice))
        loop.close()

        self.send_response(200)
        self.send_header('Content-Type', 'audio/mpeg')
        self.send_header('Content-Disposition', 'attachment; filename="speech.mp3"')
        self.end_headers()
        self.wfile.write(audio_data)

    async def _generate_tts(self, text, voice):
        communicate = edge_tts.Communicate(text, voice)
        audio_chunks = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])
        return b''.join(audio_chunks)