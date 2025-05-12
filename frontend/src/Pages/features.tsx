import FeaturesSectionDemo from "@/components/features-section-demo-2";
import { motion } from "framer-motion";
import {
  Sparkles,
  CalendarDays,
  Search,
  Target,
  MapPin,
  Clock4,
  MessageSquare,
} from "lucide-react";

const features = [
  {
    icon: <CalendarDays className="w-6 h-6 text-cyan-400" />,
    title: "Instantly Know the Agenda",
    desc: "Ask “What’s next?” and get real-time session details.",
  },
  {
    icon: <Search className="w-6 h-6 text-purple-400" />,
    title: "Discover Who’s Who",
    desc: "EventBot scans resumes (securely) to suggest participants with similar tech interests.",
  },
  {
    icon: <Target className="w-6 h-6 text-pink-400" />,
    title: "Personalized Session Recommendations",
    desc: "Get suggestions based on your skills and background.",
  },
  {
    icon: <MapPin className="w-6 h-6 text-yellow-400" />,
    title: "Location Made Simple",
    desc: "Ask about directions — EventBot guides you instantly.",
  },
  {
    icon: <Clock4 className="w-6 h-6 text-green-400" />,
    title: "Stay on Track",
    desc: "Never miss a beat — updates on breaks, lunch, and more.",
  },
  {
    icon: <MessageSquare className="w-6 h-6 text-red-400" />,
    title: "No-Form Feedback",
    desc: "Quick, conversational session feedback — no forms!",
  },
];

export default function Features() {
  return (
    <div className="h-full">
      <h2 className="text-3xl md:text-4xl font-[Playfair] text-white mb-4 mt-10 my-10 flex items-center justify-center gap-2">
        <Sparkles className="text-teal-400" /> What Can eventAlly Do?
      </h2>
      <FeaturesSectionDemo />
    </div>
    // <section className="bg-black text-white py-20 px-6 md:px-16 font-[Raleway]">
    //   <div className="max-w-5xl mx-auto text-center">
    //     <h2 className="text-3xl md:text-4xl font-[Playfair] text-white mb-4 flex items-center justify-center gap-2">
    //       <Sparkles className="text-teal-400" /> What Can EventBot Do?
    //     </h2>
    //     <p className="text-gray-400 mb-12">
    //       Meet your AI-powered event companion. Here's what it can help you with:
    //     </p>
    //     <div className="grid md:grid-cols-2 gap-8">
    //       {features.map((feature, index) => (
    //         <motion.div
    //           key={index}
    //           initial={{ opacity: 0, y: 30 }}
    //           whileInView={{ opacity: 1, y: 0 }}
    //           transition={{ duration: 0.5, delay: index * 0.1 }}
    //           whileHover={{ scale: 1.03 }}
    //           className="bg-[#0f0f0f] rounded-2xl p-6 shadow-md hover:shadow-xl transition-all duration-300 border border-gray-800"
    //         >
    //           <div className="flex items-center gap-4 mb-2">
    //             {feature.icon}
    //             <h3 className="text-lg font-semibold">{feature.title}</h3>
    //           </div>
    //           <p className="text-gray-400 text-sm">{feature.desc}</p>
    //         </motion.div>
    //       ))}
    //     </div>
    //   </div>
    // </section>
  );
}
