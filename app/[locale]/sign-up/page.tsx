"use client";

import Image from "next/image";
import { useState } from "react";
import { Loader2, X } from "lucide-react";
import { FaUserPlus } from "react-icons/fa";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { signUp } from "@/app/lib/auth-client";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { LanguageToggle } from "@/components/ui/language-toggle";
import { useLanguage } from "@/i18n/context/language-context";
import { cn } from "@/lib/utils";

export default function SignUp() {
  const { t, locale } = useLanguage();
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirmation, setPasswordConfirmation] = useState("");
  const [image, setImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleImageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setImage(file);
      const reader = new FileReader();
      reader.onloadend = () => setImagePreview(reader.result as string);
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async () => {
    if (password !== passwordConfirmation) {
      toast.error(t("auth.signUp.passwordMismatch"));
      return;
    }

    await signUp.email({
      email,
      password,
      name: `${firstName} ${lastName}`.trim(),
      image: image ? await convertImageToBase64(image) : "",
      callbackURL: `/${locale}/dashboard`,
      fetchOptions: {
        onRequest: () => setLoading(true),
        onResponse: () => setLoading(false),
        onError: (ctx) => {
          toast.error(ctx.error.message);
        },
        onSuccess: async () => {
          toast.success(t("auth.signUp.success"));
          router.push(`/${locale}/dashboard`);
        },
      },
    });
  };

  return (
    <div
      className={cn(
        "flex min-h-screen w-full flex-col items-center justify-center px-4",
        "bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-black",
      )}
    >
      <div className="absolute right-6 top-6">
        <LanguageToggle />
      </div>
      <Card
        className={cn(
          "w-full sm:w-[380px] md:w-[420px] lg:w-[460px] xl:w-[500px]",
          "rounded-2xl border border-neutral-200 bg-white shadow-lg transition-all duration-300 dark:border-neutral-800 dark:bg-neutral-900",
        )}
      >
        <CardHeader className="space-y-2 text-center">
          <CardTitle className="text-xl font-semibold md:text-2xl">{t("auth.signUp.title")}</CardTitle>
          <CardDescription className="text-sm text-muted-foreground md:text-base">
            {t("auth.signUp.description")}
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="first-name">{t("auth.signUp.firstName")}</Label>
              <Input id="first-name" placeholder="Max" required value={firstName} onChange={(event) => setFirstName(event.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="last-name">{t("auth.signUp.lastName")}</Label>
              <Input id="last-name" placeholder="Robinson" required value={lastName} onChange={(event) => setLastName(event.target.value)} />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">{t("auth.signUp.email")}</Label>
            <Input id="email" type="email" placeholder="m@example.com" required value={email} onChange={(event) => setEmail(event.target.value)} />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">{t("auth.signUp.password")}</Label>
            <Input id="password" type="password" placeholder="********" autoComplete="new-password" required value={password} onChange={(event) => setPassword(event.target.value)} />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password_confirmation">{t("auth.signUp.confirmPassword")}</Label>
            <Input id="password_confirmation" type="password" placeholder="********" autoComplete="new-password" required value={passwordConfirmation} onChange={(event) => setPasswordConfirmation(event.target.value)} />
          </div>

          <div className="space-y-2">
            <Label htmlFor="image">{t("auth.signUp.profileImage")}</Label>
            <div className="flex items-center gap-4">
              {imagePreview && (
                <div className="relative h-16 w-16 overflow-hidden rounded-md border border-neutral-200 dark:border-neutral-700">
                  <Image src={imagePreview} alt={t("auth.signUp.profilePreview")} fill className="object-cover" />
                  <button
                    type="button"
                    onClick={() => {
                      setImage(null);
                      setImagePreview(null);
                    }}
                    className="absolute right-0 top-0 rounded-bl-sm bg-black/50 p-1 text-white"
                  >
                    <X size={14} />
                  </button>
                </div>
              )}
              <Input id="image" type="file" accept="image/*" className="w-full" onChange={handleImageChange} />
            </div>
          </div>

          <Button className="mt-2 flex w-full items-center justify-center gap-2" disabled={loading} onClick={handleSubmit}>
            {loading ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <>
                <FaUserPlus className="h-4 w-4" />
                {t("auth.signUp.submit")}
              </>
            )}
          </Button>
        </CardContent>

        <CardFooter className="flex items-center justify-center border-t py-4 text-center text-xs text-neutral-500">
          {t("auth.securedBy")} <span className="ml-1 font-medium text-orange-400">better-auth</span>
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
