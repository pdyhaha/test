import os
import json
import logging
import sys
import argparse
import time
from typing import Any, Dict, Optional
import urllib.request
import urllib.error

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def normalize_message_payload(payload: Any) -> Dict[str, Any]:
    r = {}
    if isinstance(payload, dict):
        r = payload
    else:
        try:
            r = json.loads(payload)
        except Exception:
            r = {"text": str(payload)}
    cid = r.get("conversation_id") or r.get("id") or r.get("session_id")
    messages = r.get("messages")
    if isinstance(messages, list) and messages:
        parts = []
        for m in messages:
            if isinstance(m, dict):
                c = m.get("content") or m.get("text") or ""
            else:
                c = str(m)
            parts.append(str(c))
        text = "\n".join(parts)
    else:
        text = r.get("text") or r.get("content") or r.get("message") or ""
        if not isinstance(text, str):
            try:
                text = json.dumps(text, ensure_ascii=False)
            except Exception:
                text = str(text)
    return {"conversation_id": cid, "text": text}

BAD_WORDS = [
    "傻逼","妈的","操你","滚","垃圾","狗屎","sb","cnm","nmsl",
    "fuck","shit","bitch","asshole","idiot","moron","stupid","damn","fucker","motherfucker"
]

def fallback_abuse_detection(text: str) -> Dict[str, Any]:
    t = text.lower()
    hits = []
    for w in BAD_WORDS:
        if w in t or w in text:
            hits.append(w)
    score = min(1.0, len(hits) / 3.0) if hits else 0.0
    return {"contains_abuse": bool(hits), "labels": list(set(hits)), "confidence": score, "source": "fallback"}

def call_openai_moderation(text: str) -> Optional[Dict[str, Any]]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    system_prompt = "你是一个对话内容审核助手。对于给定的对话文本，判断是否包含辱骂或人身攻击，并以严格的 JSON 返回：{\"contains_abuse\": boolean, \"labels\": string[], \"confidence\": number}。只输出 JSON。"
    user_prompt = f"文本：\n{text}\n\n请输出 JSON。"
    body = {
        "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8")
            j = json.loads(raw)
            choices = j.get("choices") or []
            if not choices:
                return None
            content = choices[0].get("message", {}).get("content") or ""
            try:
                out = json.loads(content)
            except Exception:
                return None
            ca = bool(out.get("contains_abuse"))
            labels = out.get("labels") or []
            conf = out.get("confidence") or 0
            return {"contains_abuse": ca, "labels": labels, "confidence": conf, "source": "openai"}
    except urllib.error.HTTPError as e:
        return None
    except urllib.error.URLError as e:
        return None
    except Exception:
        return None

def moderate_conversation(payload: Any) -> Dict[str, Any]:
    info = normalize_message_payload(payload)
    text = info["text"] or ""
    res = call_openai_moderation(text)
    if res is None:
        res = fallback_abuse_detection(text)
    return {
        "conversation_id": info["conversation_id"],
        "contains_abuse": res["contains_abuse"],
        "labels": res["labels"],
        "confidence": res["confidence"],
        "source": res.get("source"),
        "length": len(text)
    }

def create_kafka_clients() -> Optional[Dict[str, Any]]:
    try:
        from kafka import KafkaConsumer, KafkaProducer
    except Exception:
        return None
    bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    topic = os.getenv("KAFKA_TOPIC", "qa_conversations")
    group_id = os.getenv("KAFKA_GROUP_ID", "moderation_consumer")
    res_topic = os.getenv("KAFKA_RESULT_TOPIC")
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap,
        group_id=group_id,
        enable_auto_commit=True,
        auto_offset_reset=os.getenv("KAFKA_AUTO_OFFSET_RESET", "latest"),
        value_deserializer=lambda m: m.decode("utf-8"),
        consumer_timeout_ms=int(os.getenv("KAFKA_CONSUMER_TIMEOUT_MS", "-1"))
    )
    producer = None
    if res_topic:
        producer = KafkaProducer(
            bootstrap_servers=bootstrap,
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8")
        )
    return {"consumer": consumer, "producer": producer, "result_topic": res_topic}

def run_kafka_loop():
    kp = create_kafka_clients()
    if kp is None:
        logging.error("Kafka 未安装或不可用")
        return 1
    consumer = kp["consumer"]
    producer = kp["producer"]
    result_topic = kp["result_topic"]
    for msg in consumer:
        raw = msg.value
        try:
            payload = json.loads(raw)
        except Exception:
            payload = raw
        out = moderate_conversation(payload)
        logging.info(json.dumps(out, ensure_ascii=False))
        if producer and result_topic:
            try:
                producer.send(result_topic, out)
            except Exception:
                pass
    return 0

def run_test_once():
    sample = {
        "conversation_id": "demo-1",
        "messages": [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "请问需要什么帮助"},
            {"role": "user", "content": "你这个服务太垃圾了，滚"}
        ]
    }
    out = moderate_conversation(sample)
    print(json.dumps(out, ensure_ascii=False))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    if args.test:
        run_test_once()
        return
    code = run_kafka_loop()
    if code != 0:
        sys.exit(code)

if __name__ == "__main__":
    main()

