#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebClient module for Clinical eCRF Automation (Stroke Registry)
Handles authentication, anti-bot challenge bypass (slowAES), session management, and form submissions.
"""

import urllib.request
import urllib.parse
import http.cookiejar
import re
import subprocess
import os
import tempfile
import time

def solve_challenge(html):
    """
    Solve hosting anti-bot DDoS challenge using AES decryption via macOS JavaScriptCore (osascript).
    """
    matches = re.findall(r'toNumbers\("([a-f0-9]+)"\)', html)
    if len(matches) >= 3:
        a, b, c = matches[0], matches[1], matches[2]
        
        # Locate aes.js in current directory or script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        aes_candidate = os.path.join(script_dir, 'aes.js')
        if not os.path.exists(aes_candidate):
            aes_candidate = 'aes.js'
        aes_abs_path = os.path.abspath(aes_candidate)

        solve_file = os.path.join(tempfile.gettempdir(), 'solve_challenge.js')
        js_code = f"""
ObjC.import('Foundation');
var aesJs = ObjC.unwrap($.NSString.stringWithContentsOfFileEncodingError('{aes_abs_path}', $.NSUTF8StringEncoding, null));
eval(aesJs);
function toNumbers(d) {{
    var e = [];
    d.replace(/(..)/g, function(d) {{ e.push(parseInt(d, 16)); }});
    return e;
}}
function toHex() {{
    var d = 1 == arguments.length && arguments[0].constructor == Array ? arguments[0] : arguments;
    var e = "";
    for (var f = 0; f < d.length; f++) {{
        e += (16 > d[f] ? "0" : "") + d[f].toString(16);
    }}
    return e.toLowerCase();
}}
var a = toNumbers('{a}');
var b = toNumbers('{b}');
var c = toNumbers('{c}');
toHex(slowAES.decrypt(c, 2, a, b));
"""
        with open(solve_file, 'w', encoding='utf-8') as f:
            f.write(js_code)
        
        try:
            res = subprocess.check_output(['osascript', '-l', 'JavaScript', solve_file]).decode('utf-8').strip()
            return res
        except Exception as err:
            print(f"Error solving challenge via osascript: {err}")
            return None
        finally:
            if os.path.exists(solve_file):
                try:
                    os.remove(solve_file)
                except OSError:
                    pass
    return None

class WebClient:
    def __init__(self, base_url='https://dotquyevt.freehosting.dev'):
        self.base_url = base_url.rstrip('/')
        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        self.last_url = ''

    def get(self, url, max_retries=3):
        if not url.startswith('http'):
            url = f"{self.base_url}/{url.lstrip('/')}"
        for attempt in range(max_retries):
            try:
                req = urllib.request.Request(url, headers=self.headers)
                resp = self.opener.open(req, timeout=25)
                self.last_url = resp.geturl()
                content = resp.read().decode('utf-8')
                if 'slowAES' in content:
                    val = solve_challenge(content)
                    if val:
                        domain = urllib.parse.urlparse(self.base_url).netloc
                        cookie = http.cookiejar.Cookie(
                            version=0, name='__test', value=val, port=None, port_specified=False,
                            domain=domain, domain_specified=True, domain_initial_dot=False,
                            path='/', path_specified=True, secure=False, expires=None, discard=True, comment=None,
                            comment_url=None, rest={'HttpOnly': None}, rfc2109=False
                        )
                        self.cj.set_cookie(cookie)
                        req2 = urllib.request.Request(url, headers=self.headers)
                        resp2 = self.opener.open(req2, timeout=25)
                        self.last_url = resp2.geturl()
                        content = resp2.read().decode('utf-8')
                return content
            except Exception as e:
                wait_time = 12 if '429' in str(e) else 3
                if attempt == max_retries - 1:
                    raise
                print(f"[Retry {attempt+1}/{max_retries}] GET {url} failed: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)

    def post(self, url, data, max_retries=3):
        if not url.startswith('http'):
            url = f"{self.base_url}/{url.lstrip('/')}"
        encoded_data = urllib.parse.urlencode(data).encode('utf-8')
        for attempt in range(max_retries):
            try:
                req = urllib.request.Request(url, data=encoded_data, headers=self.headers)
                resp = self.opener.open(req, timeout=25)
                self.last_url = resp.geturl()
                content = resp.read().decode('utf-8')
                if 'slowAES' in content:
                    val = solve_challenge(content)
                    if val:
                        domain = urllib.parse.urlparse(self.base_url).netloc
                        cookie = http.cookiejar.Cookie(
                            version=0, name='__test', value=val, port=None, port_specified=False,
                            domain=domain, domain_specified=True, domain_initial_dot=False,
                            path='/', path_specified=True, secure=False, expires=None, discard=True, comment=None,
                            comment_url=None, rest={'HttpOnly': None}, rfc2109=False
                        )
                        self.cj.set_cookie(cookie)
                        req2 = urllib.request.Request(url, data=encoded_data, headers=self.headers)
                        resp2 = self.opener.open(req2, timeout=25)
                        self.last_url = resp2.geturl()
                        content = resp2.read().decode('utf-8')
                return content
            except Exception as e:
                wait_time = 12 if '429' in str(e) else 3
                if attempt == max_retries - 1:
                    raise
                print(f"[Retry {attempt+1}/{max_retries}] POST {url} failed: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)

    def login(self, access_code='HV-WVDPV'):
        """
        Authenticate with the clinical registry using access code.
        """
        login_url = f"{self.base_url}/truy-cap"
        login_html = self.get(login_url)
        m = re.search(r'name="_token" value="([^"]+)"', login_html)
        if not m:
            raise Exception('Cannot find CSRF token on login page')
        token = m.group(1)
        res = self.post(login_url, {
            '_token': token,
            'access_code': access_code
        })
        return res

    def create_case(self):
        """
        Create a new blank patient record on the eCRF platform and return (case_id, response_html).
        """
        dash_url = f"{self.base_url}/bang-dieu-khien"
        dash_html = self.get(dash_url)
        m = re.search(r'action="[^"]*?/benh-an".*?name="_token" value="([^"]+)"', dash_html, re.DOTALL)
        if not m:
            m = re.search(r'name="_token" value="([^"]+)"', dash_html)
        if not m:
            raise Exception('Cannot find CSRF token on dashboard to create case')
        token = m.group(1)
        res = self.post(f"{self.base_url}/benh-an", {'_token': token})
        
        m_id = re.search(r'/benh-an/(\d+)/buoc/', self.last_url)
        if m_id:
            return int(m_id.group(1)), res
        m_id2 = re.search(r'/benh-an/(\d+)/buoc/', res)
        if m_id2:
            return int(m_id2.group(1)), res
        raise Exception(f'Could not determine new case ID. Last URL: {self.last_url}')

if __name__ == '__main__':
    client = WebClient()
    print("Testing connection to clinical registry...")
    res = client.login('HV-WVDPV')
    print("Login successful! Checking dashboard...")
    dash = client.get('/bang-dieu-khien')
    print(f"Dashboard loaded successfully! Length: {len(dash)} bytes.")
