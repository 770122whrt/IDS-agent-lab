import mongoose from 'mongoose'

type MongooseCacheType = {
  conn: typeof mongoose | null
  promise: Promise<typeof mongoose> | null
}

export async function dbConnect() {
  // atlas url + username and password + cluster name + app name
  // in public repo: const MONGODB_URI = process.env.MONGODB_URI;
  const MONGODB_URI = process.env.MONGODB_URI
  if (!MONGODB_URI) {
    throw new Error('Please define the MONGODB_URI environment variable inside .env.local')
  }

  // the first time connection is created, use the default configuration(the latter)
  // the next time, use the cached connection(the former)
  const cached: MongooseCacheType = { conn: null, promise: null }

  // if we have a connection, use it
  if (cached.conn) return cached.conn
  // if we don't have a connection, create a new one
  if (!cached.promise) {
    cached.promise = mongoose.connect(MONGODB_URI)
  }

  cached.conn = await cached.promise
  console.log('MongoDB connected') // test
  return cached.conn
}
