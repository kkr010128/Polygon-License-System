from flask import Flask, send_file, request, jsonify, send_from_directory
import tarfile, os, sqlite3, json, re, uuid, base64
from discord_webhook import DiscordWebhook, DiscordEmbed

app = Flask(__name__)

downloadCodes = {}

@app.route('/robots.txt')
def robot_to_root():
	return send_from_directory(app.static_folder, request.path[1:])

@app.route('/api/check-license', methods=["GET", "POST"])
def checkLicense():
	browser = request.user_agent.string
	accept = request.environ['HTTP_ACCEPT']
	ip = request.remote_addr
	ip2 = request.headers.get('cf-connecting-ip')

	try:
		datas = request.get_json()
		try:
			license = datas["license"]
			hwid = re.sub(r'\n', '', datas["hwid"])
			name = datas["resourcename"]
			hostname = datas["hostname"]
			if "version" in datas:
				version = datas["version"]
				if version == "1.0.5":
					connection = sqlite3.connect('/home/odroid/Desktop/Resource-Manager/database.db')
					connection.row_factory = sqlite3.Row
					cursor = connection.cursor()
					cursor.execute('SELECT * FROM polygon_manager WHERE key = "' + license + '"')
					dbData = cursor.fetchall()

					if len(dbData) > 0:
						dbData = dbData[0]
						if dbData[5] == 0:
							if dbData[2] == "none":
								cursor.execute('UPDATE polygon_manager SET HWID = "' + hwid + '" WHERE key = "' + license + '"')
								connection.commit()
							else:
								if dbData[2] != hwid:
									cursor.execute('UPDATE polygon_manager SET banned = "1" WHERE key = "' + license + '"')
									connection.commit()
									connection.close()

									webhook = DiscordWebhook(url='webhook_url')
									embed = DiscordEmbed(title="**HWID 불일치**", description="**라이센스**: %s\n**HWID**: %s\n**서버**: %s\n**리소스**: %s\n**호스트 네임**: %s\n**브라우저**: %s\n**Accept**: %s\n**IP (1)**: %s\n**IP (2)**: %s" % (license, hwid, dbData[3], name, hostname, browser, accept, ip, ip2), color='fc0335')
									embed.set_footer(text='라이센스 서버')
									embed.set_timestamp()
									webhook.add_embed(embed)
									webhook.execute()

									return jsonify(
										{
											"error": "Mismatch HWID"
										}
									)

							allowedResources = {}
							global downloadCodes
							for i in json.loads(dbData[4]):
								key = str(uuid.uuid4())
								allowedResources[i] = key
								
								downloadCodes[key] = i

							connection.close()

							webhook = DiscordWebhook(url='webhook_url')
							embed = DiscordEmbed(title="**인증 성공**", description="**라이센스**: %s\n**HWID**: %s\n**서버**: %s\n**리소스**: %s\n**호스트 네임**: %s\n**브라우저**: %s\n**Accept**: %s\n**IP (1)**: %s\n**IP (2)**: %s" % (license, hwid, dbData[3], name, hostname, browser, accept, ip, ip2), color='42f554')
							embed.set_footer(text='라이센스 서버')
							embed.set_timestamp()
							webhook.add_embed(embed)
							webhook.execute()

							return jsonify(
								{
									"success": json.dumps(allowedResources)
								}
							)
						else:
							connection.close()

							webhook = DiscordWebhook(url='webhook_url')
							embed = DiscordEmbed(title="**차단 됨**", description="**라이센스**: %s\n**HWID**: %s\n**리소스**: %s\n**호스트 네임**: %s\n**브라우저**: %s\n**Accept**: %s\n**IP (1)**: %s\n**IP (2)**: %s" % (license, hwid, name, hostname, browser, accept, ip, ip2), color='fc0335')
							embed.set_footer(text='라이센스 서버')
							embed.set_timestamp()
							webhook.add_embed(embed)
							webhook.execute()

							return jsonify(
								{
									"error": "Banned"
								}
							)
					else:
						connection.close()

						webhook = DiscordWebhook(url='webhook_url')
						embed = DiscordEmbed(title="**잘못된 라이센스 키**", description="**라이센스**: %s\n**HWID**: %s\n**리소스**: %s\n**호스트 네임**: %s\n**브라우저**: %s\n**Accept**: %s\n**IP (1)**: %s\n**IP (2)**: %s" % (license, hwid, name, hostname, browser, accept, ip, ip2), color='fc0335')
						embed.set_footer(text='라이센스 서버')
						embed.set_timestamp()
						webhook.add_embed(embed)
						webhook.execute()

						return jsonify(
							{
								"error": "Invaild License Key"
							}
						)
				else:
					webhook = DiscordWebhook(url='webhook_url')
					embed = DiscordEmbed(title="**오래된 버전**", description="**라이센스**: %s\n**HWID**: %s\n**리소스**: %s\n**호스트 네임**: %s\n**브라우저**: %s\n**Accept**: %s\n**IP (1)**: %s\n**IP (2)**: %s" % (license, hwid, name, hostname, browser, accept, ip, ip2), color='fc0335')
					embed.set_footer(text='라이센스 서버')
					embed.set_timestamp()
					webhook.add_embed(embed)
					webhook.execute()

					return jsonify(
						{
							"error": "please update script!"
						}
					)
			else:
				webhook = DiscordWebhook(url='webhook_url')
				embed = DiscordEmbed(title="**오래된 버전**", description="**라이센스**: %s\n**HWID**: %s\n**리소스**: %s\n**호스트 네임**: %s\n**브라우저**: %s\n**Accept**: %s\n**IP (1)**: %s\n**IP (2)**: %s" % (license, hwid, name, hostname, browser, accept, ip, ip2), color='fc0335')
				embed.set_footer(text='라이센스 서버')
				embed.set_timestamp()
				webhook.add_embed(embed)
				webhook.execute()

				return jsonify(
					{
						"error": "please update script!"
					}
				)
		except Exception as e:
			webhook = DiscordWebhook(url='webhook_url')
			embed = DiscordEmbed(title="**잘못된 요청**", description="**브라우저**: %s\n**Accept**: %s\n**IP (1)**: %s\n**IP (2)**: %s\n\n오류: %s" % (browser, accept, ip, ip2, e), color='fc0335')
			embed.set_footer(text='라이센스 서버')
			embed.set_timestamp()
			webhook.add_embed(embed)
			webhook.execute()

			return jsonify(
				{
					"error": "Invaild Request"
				}
			)
	except Exception as e:
		webhook = DiscordWebhook(url='webhook_url')
		embed = DiscordEmbed(title="**잘못된 요청**", description="**브라우저**: %s\n**Accept**: %s\n**IP (1)**: %s\n**IP (2)**: %s\n\n오류: %s" % (browser, accept, ip, ip2, e), color='fc0335')
		embed.set_footer(text='라이센스 서버')
		embed.set_timestamp()
		webhook.add_embed(embed)
		webhook.execute()

		return jsonify(
			{
				"error": "Invaild Request"
			}
		)

@app.route('/api/download', methods=["GET", "POST"])
def download():
	browser = request.user_agent.string
	accept = request.environ['HTTP_ACCEPT']
	ip = request.remote_addr
	ip2 = request.headers.get('cf-connecting-ip')

	try:
		datas = request.get_json()

		try:
			license = datas["license"]
			key = datas["key"]
			rsc = datas["resourcename"]

			try:
				global downloadCodes
				if downloadCodes[key]:
					name = downloadCodes[key]
					del(downloadCodes[key])
					with tarfile.open(f"/home/odroid/Desktop/Resource-Manager/exports/{name}.tar.gz", "w:gz") as tar:
						tar.add("/home/odroid/Desktop/Resource-Manager/models/" + name, arcname=os.path.basename("/home/odroid/Desktop/Resource-Manager/polygon_system"))

					webhook = DiscordWebhook(url='webhook_url')
					embed = DiscordEmbed(title="**다운로드 성공**", description="**라이센스**: %s\n**다운로드 리소스**: %s\n**리소스**: %s\n**브라우저**: %s\n**Accept**: %s\n**IP (1)**: %s\n**IP (2)**: %s" % (license, name, rsc, browser, accept, ip, ip2), color='42f554')
					embed.set_footer(text='다운로드 서버')
					embed.set_timestamp()
					webhook.add_embed(embed)
					webhook.execute()

					return send_file(f"/home/odroid/Desktop/Resource-Manager/exports/{name}.tar.gz", mimetype = "tar.gz", download_name= f"{name}.tar.gz", as_attachment = True)
				else:
					webhook = DiscordWebhook(url='webhook_url')
					embed = DiscordEmbed(title="**잘못된 다운로드 키**", description="**라이센스**: %s\n**리소스**: %s\n**브라우저**: %s\n**Accept**: %s\n**IP (1)**: %s\n**IP (2)**: %s" % (license, rsc, browser, accept, ip, ip2), color='fc0335')
					embed.set_footer(text='다운로드 서버')
					embed.set_timestamp()
					webhook.add_embed(embed)
					webhook.execute()

					return jsonify(
						{
							"error": "Invaild Download Key"
						}
					)
			except Exception as e:
				webhook = DiscordWebhook(url='webhook_url')
				embed = DiscordEmbed(title="**잘못된 다운로드 키**", description="**라이센스**: %s\n**리소스**: %s\n**브라우저**: %s\n**Accept**: %s\n**IP (1)**: %s\n**IP (2)**: %s\n\n오류: %s" % (license, rsc, browser, accept, ip, ip2, e), color='fc0335')
				embed.set_footer(text='다운로드 서버')
				embed.set_timestamp()
				webhook.add_embed(embed)
				webhook.execute()

				return jsonify(
					{
						"error": "Invaild Download Key"
					}
				)
		except Exception as e:
			webhook = DiscordWebhook(url='webhook_url')
			embed = DiscordEmbed(title="**잘못된 요청**", description="**브라우저**: %s\n**Accept**: %s\n**IP (1)**: %s\n**IP (2)**: %s\n\n오류: %s" % (browser, accept, ip, ip2, e), color='fc0335')
			embed.set_footer(text='다운로드 서버')
			embed.set_timestamp()
			webhook.add_embed(embed)
			webhook.execute()

			return jsonify(
				{
					"error": "Invaild Request"
				}
			)
	except Exception as e:
		webhook = DiscordWebhook(url='webhook_url')
		embed = DiscordEmbed(title="**잘못된 요청**", description="**브라우저**: %s\n**Accept**: %s\n**IP (1)**: %s\n**IP (2)**: %s\n\n오류: %s" % (browser, accept, ip, ip2, e), color='fc0335')
		embed.set_footer(text='다운로드 서버')
		embed.set_timestamp()
		webhook.add_embed(embed)
		webhook.execute()

		return jsonify(
			{
				"error": "Invaild Request"
			}
		)

@app.route('/api/tools/download', methods=["GET", "POST"])
def tools_download():
	try:
		datas = request.get_json()

		tool = datas["tool"]
		return send_file(f"/home/odroid/Desktop/Resource-Manager/tools/{tool}.exe", mimetype = "exe", download_name="{tool}.exe", as_attachment = True)
	except Exception as e:
		webhook = DiscordWebhook(url='webhook_url')
		embed = DiscordEmbed(title="**잘못된 요청**", description="오류: %s" % (e), color='fc0335')
		embed.set_footer(text='툴 다운로드 서버')
		embed.set_timestamp()
		webhook.add_embed(embed)
		webhook.execute()

		return jsonify(
			{
				"error": "Invaild Request"
			}
		)

if __name__ == '__main__':
	app.run()
