import requests, json, os, pwd, argparse


def main():
	try:
		f = open(f"/etc/hosts", "w")
		f.write(f"{CLIENTSETTINGS_DATA['authServer']} {SESSIONSERVER}\n")
		f.write(f"{CLIENTSETTINGS_DATA['authServer']} {AUTHSERVER}\n")
		f.close()
	except PermissionError:
		print("[!] Cant write to /etc/hosts, run this script as root")
		exit()

	data = {"token": get_token}
	redeem_token = requests.post(API_URL+"/token/redeem", data=data).json()
	if 'error' in redeem_token:
		print(redeem_token['error'])
		exit()
	real_uuid = redeem_token['uuid'].replace('-','')   
	accounts_json = {}
	newProfile = {}
	newProfile['profile'] = {
						"username" : redeem_token['mcName'],
						"token" : data['token'],
						"uuid" : real_uuid,
						"userid" : redeem_token['userId']
					}

	with open(f"/home/{os.environ['SUDO_USER']}/.minecraft/launcher_accounts.json") as launcherAccounts_json:
		launcherAccounts = json.load(launcherAccounts_json)
		accounts_json[real_uuid] = {
										"accessToken" : redeem_token['session'],
										"eligibleForMigration" : "false",
										"hasMultipleProfiles" : "false",
										"legacy" : "false",
										"localId" : real_uuid,
										"minecraftProfile" : {
												"id" : real_uuid,
												"name" : redeem_token['mcName']
										},
										"persistent" : "true",
										"remoteId" : redeem_token['userId'],
										"type" : "Mojang",
										"userProperites" : [],
										"username" : redeem_token['mcName']+"@easymc.io"
									}
		launcherAccounts['accounts'].update(accounts_json)
		with open(f"/home/{os.environ['SUDO_USER']}/.local/easymc/profiles.json", 'a') as saveProfile:
			saveProfile.write(json.dumps(newProfile, indent=2))
		with open(f"/home/{os.environ['SUDO_USER']}/.minecraft/launcher_accounts.json", 'w') as save_newProfile:
			save_newProfile.write(json.dumps(launcherAccounts, indent=2))

if __name__ == "__main__":
	API_URL = "https://api.easymc.io/v1";
	AUTHSERVER = "authserver.mojang.com";
	SESSIONSERVER = "sessionserver.mojang.com";
	CLIENTSETTINGS_DATA = requests.get(API_URL+"/client/settings").json()
	parser = argparse.ArgumentParser()
	parser.add_argument('-t', '--token', help='Account token for easymc')
	args = parser.parse_args()
	if args.token:
		get_token = args.token
		print(get_token)
	else:
		print("No token given")
		exit()
	main()
