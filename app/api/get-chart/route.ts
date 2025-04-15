import { MongoClient, ServerApiVersion } from 'mongodb';
import { NextRequest, NextResponse } from 'next/server';

// Cache the database connection this time
let cachedClient: MongoClient | null = null;

async function connectToDatabase() {
    if (cachedClient) {
        return cachedClient;
    }
    const uri = `mongodb+srv://get-data:QTD0djmF1PlFdrkK@bera.1e3b4.mongodb.net/?retryWrites=true&w=majority&appName=Bera`; // stored in Vercel, not the git repo this time.
    
    if (!uri) {
        throw new Error('Please define the MONGODB_URI environment variable');
    }

    const client = new MongoClient(uri, {
        serverApi: {
            version: ServerApiVersion.v1,
            strict: true,
            deprecationErrors: true,
        }
    });

    await client.connect();
    cachedClient = client;
    return client;
}

export async function GET(request: NextRequest) {
    try {
        // Get the metric being charted from query parameters
        const searchParams = request.nextUrl.searchParams;
        const metric = searchParams.get('metric');
        const dateFrom = searchParams.get('dateFrom');
        const dateTo = searchParams.get('dateTo');

        if (!metric) {
            return NextResponse.json(
                { error: 'Metric parameter is required' },
                { status: 400 }
            );
        }

        // Connect to the database
        const client = await connectToDatabase();
        const db = client.db('Bera'); // fixme andrej: maybe make this an environment variable?
        
        // Validate that the metric exists in the schema
        const validSignalMetrics = [
            'bitsPerPacket',
            'numPackets',
            'bitErrorRate',
            'bitsSent',
            'bitsReceived',
            'power'
        ];

        const validWeatherMetrics = [
            'temperature',
            'relativeHumidity',
            'precipitation',
            'barometricPressure',
            'dewpoint'
        ]
        
        // Determine which collection to use based on the metric
        const collectionName = validSignalMetrics.includes(metric) ? 'Radio' : 'CWRU';
        const collection = db.collection(collectionName);
            
        if (!validSignalMetrics.includes(metric) && !validWeatherMetrics.includes(metric)) {
            return NextResponse.json(
                { error: `Invalid metric. Choose one of: ${validSignalMetrics.join(', ')} or ${validWeatherMetrics.join(', ')}` },
                { status: 400 }
            );
        }

        // Build query with date range if provided
        const query: any = {};
        if (dateFrom || dateTo) {
            query.timestamp = {};
            if (dateFrom) {
                query.timestamp.$gte = new Date(dateFrom);
            }
            if (dateTo) {
                query.timestamp.$lte = new Date(dateTo);
            }
        }
        // If no date range is provided, default to the last 24 hours
        if (!dateFrom && !dateTo) {
            const now = new Date();
            const twentyFourHoursAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
            query.timestamp = {
                $gte: twentyFourHoursAgo,
                $lte: now
            };
        }

        // Query the data - get timestamp and the requested metric
        const projection: Record<string, number> = {
            timestamp: 1,
            _id: 0
        };
        projection[metric] = 1;

        const data = await collection
            .find(query)
            .project(projection)
            .sort({ timestamp: 1 })
            .toArray();

        // Format the response
        const chartData = {
            x: data.map(item => item.timestamp),
            y: data.map(item => item[metric]),
        };

        return NextResponse.json(chartData, {
            headers: {
                'Cache-Control': 'no-store',
            },
        });
    } catch (error) {
        console.error('Database error:', error);
        return NextResponse.json(
            { error: 'Failed to fetch chart data' },
            { status: 500 }
        );
    }
}