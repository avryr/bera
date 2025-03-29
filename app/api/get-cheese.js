export function GET(request) {
    //return new Response('Cheddar');
    return new Response('Cheddar', {
        headers: {
            'Content-Type': 'text/plain',
            'Cache-Control': 'no-store',
            'X-Custom-Header': 'my-custom-value',
        },
    });
  }