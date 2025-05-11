// import { Particles } from "@/components/magicui/particles";
import { Cover } from "@/components/ui/cover";
import { useNavigate } from "react-router-dom";
import { ShimmerButton } from "@/components/magicui/shimmer-button";
import { LineShadowText } from "@/components/magicui/line-shadow-text";

// style={{ background: "radial-gradient(circle at top, #161d19, #4b405e)"

const HeroSection = () => {
  const nav = useNavigate();
  return (
    <div className="relative flex min-h-screen w-full flex-col items-center justify-center overflow-hidden bg-[url(./assets/gradient_backdrop.png)] bg-cover bg-fixed bg-center bg-no-repeat bg-background">
      <div className="flex flex-col justify-center h-full items-center">
        <span className="font-playfair text-[#dad5dbe1] pointer-events-none z-10 whitespace-pre-wrap text-center leading-none">
          <span className="font-extralitght text-9xl italic">smarter </span>{" "}
          <span className="font-semibold font-raleway text-9xl bg-gradient-to-b">
            Events
          </span>
        </span>
        <span className="text-3xl font-raleway text-[#D1D5DB] italic  ml-140">
          Seamless Experiences
        </span>
        <span className="font-playfair text-[#edd1f3e1] text-3xl text-center mt-4 ml-30">
          powered by{" "}
          <span className="text-8xl font-raleway font-extrabold italic">
            <Cover>
            <LineShadowText className="italic" shadowColor="#edd1f3e1">
              YOU
            </LineShadowText>

            </Cover>
            {/* <LineShadowText className="italic" shadowColor="#edd1f3e1">
              YOU
            </LineShadowText> */}
          </span>
        </span>

        <div className="mt-8">
          <ShimmerButton className="shadow-2xl px-4 py-2 mt-10" onClick={()=>nav("/chat")}>
            <span className="font-playfair text-center text-sm font-medium leading-none tracking-tight text-white dark:from-white dark:to-slate-900/10 lg:text-2xl">
              Get Started -
            </span>
          </ShimmerButton>
        </div>
      </div>
    </div>
  );
};

export default HeroSection;
