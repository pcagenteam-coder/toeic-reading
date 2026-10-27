"""双端点 LLM 调用：Kunyou + igrok，各自 ≤10 并发（信号量，用户要求），失败互为备援。凭据由网关注入。"""
import json, re, subprocess, threading, time
EPS = {'kunyou': ('https://api.kunyou.asia/v1/chat/completions', 'deepseek-v4.1-flash-1017'),
       'igrok': ('https://igrok.lvyrix.com/v1/chat/completions', 'deepseek-v4.1-flash')}
SEM = {k: threading.BoundedSemaphore(10) for k in EPS}


def _call(ep, msgs, max_tokens, temp, timeout):
    url, model = EPS[ep]
    body = json.dumps({'model': model, 'messages': msgs, 'max_tokens': max_tokens, 'temperature': temp,
                       'response_format': {'type': 'json_object'}})
    with SEM[ep]:
        r = subprocess.run(['curl', '-s', '--max-time', str(timeout), url, '-H', 'Content-Type: application/json', '-d', '@-'],
                           input=body, capture_output=True, text=True, timeout=timeout + 10)
    try:
        ch = json.loads(r.stdout)['choices'][0]
    except Exception:
        raise RuntimeError(f'{ep} raw={r.stdout[:120]!r}')
    c = (ch['message'].get('content') or '').strip()
    c = re.sub(r'^```(json)?|```$', '', c).strip()
    m = re.search(r'\{.*\}', c, re.S)
    if not m:
        raise RuntimeError(f'{ep} finish={ch.get("finish_reason")} content={c[:80]!r}')
    return json.loads(m.group(0))


def chat(msgs, max_tokens=6000, temp=0.7, prefer='kunyou', timeout=400, tries=4):
    order = [prefer] + [k for k in EPS if k != prefer]
    err = None
    for a in range(tries):
        ep = order[a % 2]
        try:
            return _call(ep, msgs, max_tokens, temp, timeout)
        except Exception as e:
            err = e
            time.sleep(1 + 2 * a)
    raise RuntimeError(f'api fail: {err}')
