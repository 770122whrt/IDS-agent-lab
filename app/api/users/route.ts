// from server API of Next.js import some types and utilities
// NextRequest: represents the incoming HTTP request object (similar to traditional req)
// NextResponse: used to construct the HTTP response object (similar to traditional res)
import { dbConnect } from 'backend/mongodb'
import { User } from 'backend/user'
import { type NextRequest, NextResponse } from 'next/server'

// import the User Mongoose model (packed in lib/User.ts)

// define an async function GET (READ)
// —— Next.js will automatically recognize this as a GET request handler for the API route
export async function GET() {
  //req: NextRequest
  try {
    // First step: connect to the MongoDB database
    // dbConnect usually wraps Mongoose.connect() with *caching* logic,
    // so that a new connection is not created on every API call.
    await dbConnect()

    // Second step: query all users from the database
    // User is a Mongoose model (similar to a MongoDB collection mapping)
    // find({}) means to find all documents
    const users = await User.find({})

    // Third step: return a JSON response
    // NextResponse.json() will automatically set the content-type to application/json
    return NextResponse.json(users)
  } catch (error) {
    // if any error occurs during the process. Same level as try
    return NextResponse.json({ error: 'Failed to fetch users' }, { status: 500 })
  }
}

// POST - create user (CREATE)
export async function POST(req: NextRequest) {
  try {
    await dbConnect()

    // read json from request body
    const body = await req.json()
    const { name, email, password } = body

    const newUser = await User.create({ name, email, password })
    // return the created user with 201 status code
    return NextResponse.json(newUser, { status: 201 })
  } catch (error) {
    return NextResponse.json({ error: 'Failed to create user' }, { status: 500 })
  }
}
