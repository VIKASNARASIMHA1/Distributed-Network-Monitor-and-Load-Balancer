#!/usr/bin/env python3
"""
Traffic Generator - Simulates traffic for testing load balancer
"""
import requests
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
import statistics
from datetime import datetime

class TrafficGenerator:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.stats = {
            'total_requests': 0,
            'successful': 0,
            'failed': 0,
            'response_times': [],
        }
        self.lock = threading.Lock()
    
    def send_request(self, request_id: int) -> Dict:
        """Send a single request to load balancer"""
        start_time = time.time()
        
        try:
            response = requests.get(
                f"{self.base_url}/request",
                timeout=10,
                headers={'User-Agent': f'TrafficGenerator/{request_id}'}
            )
            
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            with self.lock:
                self.stats['total_requests'] += 1
                
                if response.status_code == 200:
                    self.stats['successful'] += 1
                    result = {
                        'success': True,
                        'request_id': request_id,
                        'response_time': response_time,
                        'data': response.json(),
                    }
                else:
                    self.stats['failed'] += 1
                    result = {
                        'success': False,
                        'request_id': request_id,
                        'response_time': response_time,
                        'status_code': response.status_code,
                    }
                
                self.stats['response_times'].append(response_time)
                return result
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            with self.lock:
                self.stats['total_requests'] += 1
                self.stats['failed'] += 1
                self.stats['response_times'].append(response_time)
                
                return {
                    'success': False,
                    'request_id': request_id,
                    'response_time': response_time,
                    'error': str(e),
                }
    
    def generate_traffic(self, num_requests: int, concurrency: int = 10) -> List[Dict]:
        """Generate traffic with specified concurrency"""
        print(f"🚀 Generating {num_requests} requests with {concurrency} concurrent workers...")
        
        results = []
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            # Submit all requests
            futures = {
                executor.submit(self.send_request, i): i
                for i in range(num_requests)
            }
            
            # Process results as they complete
            for future in as_completed(futures):
                request_id = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Show progress
                    if len(results) % 100 == 0:
                        print(f"📈 Processed {len(results)}/{num_requests} requests")
                        
                except Exception as e:
                    print(f"❌ Error processing request {request_id}: {e}")
        
        return results
    
    def print_stats(self):
        """Print statistics"""
        print("\n" + "="*50)
        print("📊 TRAFFIC GENERATION STATISTICS")
        print("="*50)
        
        with self.lock:
            total = self.stats['total_requests']
            successful = self.stats['successful']
            failed = self.stats['failed']
            
            print(f"Total Requests:     {total}")
            print(f"Successful:         {successful} ({successful/total*100:.1f}%)")
            print(f"Failed:             {failed} ({failed/total*100:.1f}%)")
            
            if self.stats['response_times']:
                avg_time = statistics.mean(self.stats['response_times'])
                min_time = min(self.stats['response_times'])
                max_time = max(self.stats['response_times'])
                
                print(f"Avg Response Time:  {avg_time:.2f}ms")
                print(f"Min Response Time:  {min_time:.2f}ms")
                print(f"Max Response Time:  {max_time:.2f}ms")
            
            print("="*50)
    
    def continuous_traffic(self, requests_per_minute: int, duration_minutes: int):
        """Generate continuous traffic for specified duration"""
        print(f"🔄 Generating continuous traffic: {requests_per_minute} RPM for {duration_minutes} minutes")
        
        end_time = time.time() + (duration_minutes * 60)
        request_count = 0
        
        while time.time() < end_time:
            # Calculate requests per second for this interval
            requests_per_second = requests_per_minute / 60
            interval = 1.0 / requests_per_second
            
            # Send requests for this second
            start = time.time()
            requests_sent = 0
            
            while time.time() - start < 1.0 and requests_sent < requests_per_second:
                self.send_request(request_count)
                request_count += 1
                requests_sent += 1
                
                # Sleep to maintain rate
                time.sleep(interval)
            
            # Print progress every 10 seconds
            if int(time.time()) % 10 == 0:
                elapsed = (duration_minutes * 60) - (end_time - time.time())
                remaining = end_time - time.time()
                
                print(f"⏱️  Elapsed: {elapsed/60:.1f}min, Remaining: {remaining/60:.1f}min, "
                      f"Requests: {request_count}")
        
        print("✅ Continuous traffic generation complete")
        self.print_stats()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Traffic Generator for Load Balancer Testing')
    parser.add_argument('--requests', '-r', type=int, default=1000,
                       help='Total number of requests to send')
    parser.add_argument('--concurrent', '-c', type=int, default=10,
                       help='Number of concurrent requests')
    parser.add_argument('--continuous', action='store_true',
                       help='Generate continuous traffic')
    parser.add_argument('--rpm', type=int, default=600,
                       help='Requests per minute for continuous mode')
    parser.add_argument('--duration', type=int, default=5,
                       help='Duration in minutes for continuous mode')
    parser.add_argument('--url', type=str, default='http://localhost:5000',
                       help='Load balancer URL')
    
    args = parser.parse_args()
    
    generator = TrafficGenerator(base_url=args.url)
    
    try:
        if args.continuous:
            generator.continuous_traffic(args.rpm, args.duration)
        else:
            results = generator.generate_traffic(args.requests, args.concurrent)
            generator.print_stats()
            
            # Print some sample results
            print("\n🎯 Sample Results:")
            for result in results[:5]:
                if result['success']:
                    print(f"  Request {result['request_id']}: "
                          f"{result['response_time']:.2f}ms - "
                          f"Server: {result['data'].get('server_name', 'N/A')}")
                else:
                    print(f"  Request {result['request_id']}: "
                          f"FAILED - {result.get('error', 'Unknown error')}")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Traffic generation interrupted by user")
        generator.print_stats()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        generator.print_stats()

if __name__ == "__main__":
    main()