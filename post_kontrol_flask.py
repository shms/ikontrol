from flask import Flask, render_template, request
import json
import requests
import re
from donustur import donustur

app = Flask(__name__)


def get_comment_usernames(media_id, min_id=None):
    headers = {
        'x-ig-app-locale': 'tr_TR',
        'x-ig-device-locale': 'tr_TR',
        'x-ig-mapped-locale': 'tr_TR',
        'x-ig-android-id': 'android-e936d1ee51cf3533',
        'x-ig-nav-chain': 'ExploreFragment:explore_popular:2:main_search:1699891038.348::,SingleSearchTypeaheadTabFragment:search_typeahead:20:button:1699898584.895::,UserDetailFragment:profile:21:search_result:1699898585.887::,ProfileMediaTabFragment:profile:22:button:1699898588.87::,ContextualFeedFragment:feed_contextual:23:button:1699898598.268::,InteractivityBottomSheetFragment:feed_contextual_profile:24:button:1699898608.895::',
        'x-fb-connection-type': 'WIFI',
        'x-ig-connection-type': 'WIFI',
        'x-ig-capabilities': '3brTv10=',
        'x-ig-app-id': '567067343352427',
        'user-agent': 'Instagram 307.0.0.34.111 Android (28/9; 360dpi; 1080x1920; Asus; ASUS_I003DD; ASUS_I003DD; intel; tr_TR; 532277890)',
        'accept-language': 'tr-TR, en-US',
        'authorization': 'Bearer IGT:2:eyJkc191c2VyX2lkIjoiNjM0MzE3MjIwMDciLCJzZXNzaW9uaWQiOiI2MzQzMTcyMjAwNyUzQURLQW1UM0lYVkE5OFM5JTNBOSUzQUFZYzY3Tml2ckJGUk02WFVULVdXNFNCQUZpMXZLaDRxcjFmcTU4NURxdyJ9',
        'x-fb-http-engine': 'Liger',
        'x-fb-client-ip': 'True',
        'x-fb-server-cluster': 'True',
    }

    params = {
        'min_id': min_id,
        'sort_order': 'popular',
        'analytics_module': 'comments_v2_feed_contextual_profile',
        'can_support_threading': 'true',
        'is_carousel_bumped_post': 'false',
        'feed_position': '0',
    }

    usernames = set()  # Using a set to avoid duplicate usernames

    while True:
        # Örnek bir HTTP isteği gönderme
        response = requests.get(
            f'https://i.instagram.com/api/v1/media/{media_id}/stream_comments/',
            params=params,
            headers=headers,
        )

        # Yanıtı satır satır ayırma
        lines = response.text.splitlines()

        # Her bir satırı ayrı ayrı JSON olarak çözümleme
        for line in lines:
            try:
                json_data = json.loads(line)
                # Kullanıcı adlarını ekrana yazdırma
                for comment in json_data.get('comments', []):
                    username = comment.get('user', {}).get('username')
                    if username:
                        usernames.add(username)
            except json.JSONDecodeError as e:
                print(f"Hata: {e}")

        # Check if there is more data to fetch
        next_min_id = json_data.get('next_min_id')
        if not next_min_id:
            break

        # Update the min_id for the next request
        params['min_id'] = next_min_id

    return usernames


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        link = request.form['post_link']
        als = donustur(link)  # 'donustur' fonksiyonunun geri kalanı
        media_id = als  # media_id'nin elde edildiği kısım
        all_usernames = get_comment_usernames(media_id)  # Kullanıcı adlarını çeken kısım

        grup_uye = request.form['grup_uye']  # Grup üye textarea'sından gelen veri
        grup_uye_kullanicilar = set(grup_uye.split())  # Boşluklara göre kullanıcı adlarını ayır

        # Eksik kullanıcı adlarını belirle
        eksik_kullanicilar = all_usernames - grup_uye_kullanicilar

        # İzinli kullanıcı adlarını kontrol et ve eksiklerden sil
        izinli_uye = request.form['izinliler']  # Grup üye textarea'sından gelen veri
        izinli_uyelerr = set(izinli_uye.split())  # Boşluklara göre kullanıcı adlarını ayır

        updated_eksikler = eksik_kullanicilar - izinli_uyelerr

        return render_template('result.html', eksikler=updated_eksikler)  # Sonuçları template'e aktar

    return render_template('form.html')  # Form sayfasını göster



if __name__ == '__main__':
    app.run(debug=True)
