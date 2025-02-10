import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import winston from 'winston';
import newrelic from 'newrelic';

// Configure logger
const logger = winston.createLogger({
    level: 'info',
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
    ),
    transports: [
        new winston.transports.Console(),
        new winston.transports.File({ filename: 'error.log', level: 'error' }),
        new winston.transports.File({ filename: 'combined.log' })
    ]
});

const app = express();

// Middleware
app.use(cors());
app.use(helmet());
app.use(morgan('combined'));
app.use(express.json());

// Health check endpoint
app.get('/health', (req: Request, res: Response) => {
    res.status(200).json({ status: 'healthy' });
});

// Metrics endpoint for Prometheus
app.get('/metrics', (req: Request, res: Response) => {
    res.set('Content-Type', newrelic.getLicenseKey() ? 'text/plain' : 'application/json');
    res.status(200).send(newrelic.getLicenseKey() ? 
        'app_requests_total{status="200"} 1\n' : 
        { message: 'Metrics not available - New Relic not configured' }
    );
});

// Main API endpoint
app.get('/api', (req: Request, res: Response) => {
    logger.info('API endpoint accessed');
    res.status(200).json({
        message: 'Welcome to Addi-Aire API',
        version: '1.0.0',
        environment: process.env.NODE_ENV
    });
});

// Error handling middleware
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
    logger.error('Error occurred:', err);
    res.status(500).json({
        error: 'Internal Server Error',
        message: process.env.NODE_ENV === 'development' ? err.message : undefined
    });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    logger.info(`Server running on port ${PORT} in ${process.env.NODE_ENV} mode`);
}); 