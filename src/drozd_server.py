from flask import Flask, request, jsonify
import json
import threading

class DrozdInfo:
	def __load_config(self, path) -> dict:
		input_dict = {}

		with open(path, encoding="utf-8") as input_file:
			input_dict = json.load(input_file)

		return input_dict

	def __init__(self, model_path: str):
		info_dict = self.__load_config(f"{model_path}/drozd.json")
		self.model_name = info_dict["model_name"]
		self.model_description = info_dict["model_description"]

class DrozdServer:
	def __init__(self, info: DrozdInfo, on_prompt):
		self.info = info
		self.app = Flask(f"drozdai_srv_{info.model_name}")
		self.on_prompt = on_prompt
		self.model_lock = threading.Lock()

		@self.app.route("/status")
		def r_status():
			return jsonify({"busy": self.model_lock.locked()})

		@self.app.route("/about")
		def r_about():
			return jsonify({
				"model_name": info.model_name,
				"model_description": info.model_description
			})

		@self.app.route("/prompt", methods=['GET'])
		def r_prompt():
			if not self.model_lock.acquire(blocking=False):
				return jsonify({
					'error': 'MODEL_IS_BUSY',
					'retry_after': 3
				}), 503, {'Retry-After': '3'}

			try:
				prompt = request.args.get("prompt")
				temperature = float(request.args.get("temperature"))
				length = int(request.args.get("len"))
				return jsonify({
					'error': None,
					"message": on_prompt(prompt, temperature, length)
				})
			finally:
				self.model_lock.release()

	def run(self, host: str, port: int):
		self.app.run(host=host, port=port)

if __name__ == "__main__":
	exit()