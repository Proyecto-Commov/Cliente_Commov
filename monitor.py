#!/usr/bin/env python3
"""
Monitor script to check system health and performance
"""
import requests
import time
import json

def monitor():
    url = "http://localhost:8080/health"
    
    print("=" * 60)
    print("[MONITOR] Sistema de Monitoreo")
    print("=" * 60)
    print("Verificando estado del sistema cada 2 segundos...")
    print("Presiona Ctrl+C para detener\n")
    
    try:
        while True:
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    status = "[OK]" if data['h264_connected'] else "[WAITING]"
                    queue = data['queue_size']
                    
                    # Mostrar estado
                    print(f"\r{status} H.264: {data['h264_connected']} | Queue: {queue}/200 | Status: {data['status']}", end="", flush=True)
                    
                    # Advertencias
                    if queue > 150:
                        print("\n[WARNING] Queue muy llena - Puede haber lag")
                    elif queue == 0 and data['h264_connected']:
                        print("\n[WARNING] Queue vacia - Esperando datos")
                else:
                    print(f"\r[ERROR] HTTP {response.status_code}", end="", flush=True)
            except requests.exceptions.ConnectionError:
                print("\r[ERROR] No se puede conectar a http://localhost:8080", end="", flush=True)
            except Exception as e:
                print(f"\r[ERROR] {str(e)[:40]}", end="", flush=True)
            
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n\n[STOP] Monitor detenido")

if __name__ == "__main__":
    monitor()
