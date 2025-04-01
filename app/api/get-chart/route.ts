import { MongoClient, ServerApiVersion } from 'mongodb';
import { NextRequest, NextResponse } from 'next/server';

// Cache the database connection this time
let cachedClient: MongoClient | null = null;

async function connectToDatabase() {
    if (cachedClient) {
        return cachedClient;
    }

    const uri = process.env.MONGODB_URI; // stored in Vercel, not the git repo this time.
    
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

        if (!metric) {
            return NextResponse.json(
                { error: 'Metric parameter is required' },
                { status: 400 }
            );
        }

        // Connect to the database
        const client = await connectToDatabase();
        const db = client.db('Bera'); // fixme andrej: maybe make this an environment variable?
        const collection = db.collection('Radio'); // fixme andrej: maybe make this an environment variable?

        // Validate that the metric exists in the schema
        const validMetrics = [
            'bitsPerPacket',
            'numPackets',
            'bitErrorRate',
            'bitsSent',
            'bitsReceived',
            'mode',
            'power'
        ];

        if (!validMetrics.includes(metric)) {
            return NextResponse.json(
                { error: `Invalid metric. Choose one of: ${validMetrics.join(', ')}` },
                { status: 400 }
            );
        }

        // Query the data - get timestamp and the requested metric
        const projection: Record<string, number> = {
            timestamp: 1,
            _id: 0
        };
        projection[metric] = 1;

        const data = await collection
            .find({})
            .project(projection)
            .sort({ timestamp: 1 })
            .toArray();

        // DEBUG: log entire collection
        const allData = await collection.find({}).toArray();
        console.log('All data:', allData);
        // DEBUG: log the data being sent to the client
        console.log('Data being sent to the client:', data);

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