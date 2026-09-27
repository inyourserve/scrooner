import { cva, type VariantProps } from "class-variance-authority";
import type { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

const cardVariants = cva("ds-card", {
  variants: {
    variant: {
      default: "",
      subtle: "ds-card--subtle",
      raised: "ds-card--raised",
    },
    interactive: {
      true: "ds-card--interactive",
      false: "",
    },
  },
  defaultVariants: { variant: "default", interactive: false },
});

type CardProps = HTMLAttributes<HTMLDivElement> & VariantProps<typeof cardVariants>;

export function Card({ variant, interactive, className, ...props }: CardProps) {
  return <div data-slot="card" className={cn(cardVariants({ variant, interactive }), className)} {...props} />;
}

export function CardHeader({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div data-slot="card-header" className={cn("ds-card__header", className)} {...props} />;
}

export function CardHeading({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div data-slot="card-heading" className={cn("ds-card__heading", className)} {...props} />;
}

export function CardTitle({ className, ...props }: HTMLAttributes<HTMLHeadingElement>) {
  return <h2 data-slot="card-title" className={cn("ds-card__title", className)} {...props} />;
}

export function CardDescription({ className, ...props }: HTMLAttributes<HTMLParagraphElement>) {
  return <p data-slot="card-description" className={cn("ds-card__description", className)} {...props} />;
}

export function CardContent({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div data-slot="card-content" className={cn("ds-card__content", className)} {...props} />;
}

export function CardFooter({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div data-slot="card-footer" className={cn("ds-card__footer", className)} {...props} />;
}
