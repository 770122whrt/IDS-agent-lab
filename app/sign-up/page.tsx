"use client";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardDescription,
  CardFooter,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useState } from "react";
import Image from "next/image";
import { Loader2, X } from "lucide-react";
import { signUp } from "@/app/lib/auth-client";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { FaUserPlus } from "react-icons/fa";

export default function SignUp() {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirmation, setPasswordConfirmation] = useState("");
  const [image, setImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImage(file);
      const reader = new FileReader();
      reader.onloadend = () => setImagePreview(reader.result as string);
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async () => {
    if (password !== passwordConfirmation) {
      toast.error("Passwords do not match");
      return;
    }

    await signUp.email({
      email,
      password,
      name: `${firstName} ${lastName}`,
      image: image ? await convertImageToBase64(image) : "",
      callbackURL: "/dashboard",
      fetchOptions: {
        onRequest: () => setLoading(true),
        onResponse: () => setLoading(false),
        onError: (ctx) => {
          toast.error(ctx.error.message);
        },
        onSuccess: async () => {
          toast.success("Account created successfully!");
          router.push("/dashboard");
        },
      },
    });
  };

  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center min-h-screen w-full px-4",
        "bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-black"
      )}
    >
      <Card
        className={cn(
          "w-full sm:w-[380px] md:w-[420px] lg:w-[460px] xl:w-[500px]",
          "shadow-lg rounded-2xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 transition-all duration-300"
        )}
      >
        <CardHeader className="text-center space-y-2">
          <CardTitle className="text-xl md:text-2xl font-semibold">
            Create an Account
          </CardTitle>
          <CardDescription className="text-sm md:text-base text-muted-foreground">
            Enter your details to get started
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Name */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="first-name">First name</Label>
              <Input
                id="first-name"
                placeholder="Max"
                required
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="last-name">Last name</Label>
              <Input
                id="last-name"
                placeholder="Robinson"
                required
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
              />
            </div>
          </div>

          {/* Email */}
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="m@example.com"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          {/* Password */}
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              placeholder="••••••••"
              autoComplete="new-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {/* Confirm Password */}
          <div className="space-y-2">
            <Label htmlFor="password_confirmation">Confirm Password</Label>
            <Input
              id="password_confirmation"
              type="password"
              placeholder="••••••••"
              autoComplete="new-password"
              required
              value={passwordConfirmation}
              onChange={(e) => setPasswordConfirmation(e.target.value)}
            />
          </div>

          {/* Profile Image */}
          <div className="space-y-2">
            <Label htmlFor="image">Profile image (optional)</Label>
            <div className="flex items-center gap-4">
              {imagePreview && (
                <div className="relative w-16 h-16 rounded-md overflow-hidden border border-neutral-200 dark:border-neutral-700">
                  <Image
                    src={imagePreview}
                    alt="Profile preview"
                    fill
                    className="object-cover"
                  />
                  <button
                    onClick={() => {
                      setImage(null);
                      setImagePreview(null);
                    }}
                    className="absolute top-0 right-0 p-1 bg-black/50 text-white rounded-bl-sm"
                  >
                    <X size={14} />
                  </button>
                </div>
              )}
              <Input
                id="image"
                type="file"
                accept="image/*"
                className="w-full"
                onChange={handleImageChange}
              />
            </div>
          </div>

          {/* Submit Button */}
          <Button
            className="w-full mt-2 flex items-center justify-center gap-2"
            disabled={loading}
            onClick={handleSubmit}
          >
            {loading ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <>
                <FaUserPlus className="w-4 h-4" />
                Create account
              </>
            )}
          </Button>
        </CardContent>

        <CardFooter className="border-t py-4 flex justify-center items-center text-center text-xs text-neutral-500">
          Secured by{" "}
          <span className="text-orange-400 font-medium ml-1">better-auth</span>
        </CardFooter>
      </Card>
    </div>
  );
}

async function convertImageToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}
