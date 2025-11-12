import { toNodeHandler } from "better-auth/node"
import { auth } from "../../lib/auth"

// Disallow body parsing, we will parse it manually
// set to 
export const config = { api: { bodyParser: false } }

export default toNodeHandler(auth.handler)