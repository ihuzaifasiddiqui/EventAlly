import React from "react";
import { cn } from "../lib/utils";
import {
  CalendarClock,
  Users,
  Target,
  MapPin,
  Clock4,
  MessageSquare,
  Sparkles,
  InfoIcon,
} from "lucide-react";

export default function FeaturesSection() {
  const features = [
    {
      title: "Instantly Know the Agenda",
      description: 'Ask "What\'s next?" and get real-time session details.',
      icon: <CalendarClock className="w-7 h-7" />,
    },
    {
      title: "No-Form Feedback",
      description: "Quick, conversational session feedback — no forms!",
      icon: <MessageSquare className="w-7 h-7" />,
    },
    {
      title: "Discover Who's Who",
      description:
        "EventBot scans resumes (securely) to suggest participants with similar tech interests.",
      icon: <Users className="w-7 h-7" />,
    },
    {
      title: "Location Made Simple",
      description: "Ask about directions — EventBot guides you instantly.",
      icon: <MapPin className="w-7 h-7" />,
    },
    {
      title: "Personalized Recommendations",
      description: "Get session suggestions based on your skills and background.",
      icon: <Target className="w-7 h-7" />,
    },
    {
      title: "Stay on Track",
      description: "Never miss a beat — updates on breaks, lunch, and more.",
      icon: <Clock4 className="w-7 h-7" />,
    },
    {
      title: "AI-Powered Experience",
      description: "Conversational, smart, and always ready to help.",
      icon: <Sparkles className="w-7 h-7" />,
    },
    {
      title: "Need Anything Else?",
      description: "Just ask! EventBot is always ready to assist you.",
      icon: <InfoIcon className="w-7 h-7" />,
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 relative z-10 py-16 max-w-7xl mx-auto">
      {features.map((feature, index) => (
        <Feature key={feature.title} {...feature} index={index} />
      ))}
    </div>
  );
}

const Feature = ({
  title,
  description,
  icon,
  index,
}: {
  title: string;
  description: string;
  icon: React.ReactNode;
  index: number;
}) => {
  // For 3 columns, first items in each row have indices 0, 3, 6
  const isFirstInRow = index % 3 === 0;
  // For 3 columns with 8 items, the first two rows are indices 0-5
  const isInTopRows = index < 6;

  return (
    <div
      className={cn(
        "flex flex-col lg:border-r py-12 relative group/feature border-neutral-800",
        isFirstInRow && "lg:border-l border-neutral-800",
        isInTopRows && "lg:border-b border-neutral-800"
      )}
    >
      {isInTopRows && (
        <div className="opacity-0 group-hover/feature:opacity-100 transition duration-200 absolute inset-0 h-full w-full bg-gradient-to-t from-neutral-800 to-transparent pointer-events-none" />
      )}
      {!isInTopRows && (
        <div className="opacity-0 group-hover/feature:opacity-100 transition duration-200 absolute inset-0 h-full w-full bg-gradient-to-b from-neutral-800 to-transparent pointer-events-none" />
      )}
      <div className="mb-5 relative z-10 px-12 text-neutral-400">
        {icon}
      </div>
      <div className="text-xl font-bold mb-3 relative z-10 px-12">
        <div className="absolute left-0 inset-y-0 h-7 group-hover/feature:h-9 w-1.5 rounded-tr-full rounded-br-full bg-neutral-700 group-hover/feature:bg-blue-500 transition-all duration-200 origin-center" />
        <span className="group-hover/feature:translate-x-2 transition duration-200 inline-block text-neutral-100">
          {title}
        </span>
      </div>
      <p className="text-base text-neutral-300 max-w-xs relative z-10 px-12">
        {description}
      </p>
    </div>
  );
}