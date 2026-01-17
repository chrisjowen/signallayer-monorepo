<script lang="ts">
	import { Button } from "$lib/components/ui/button";
	import { 
		ShieldCheck, 
		Zap, 
		ArrowRight, 
		Code2, 
		Database, 
		Search,
		Cpu,
		Fingerprint,
		Terminal
	} from "@lucide/svelte";
	import { onMount } from "svelte";

	let mounted = $state(false);

	onMount(() => {
		mounted = true;
	});
</script>

<div class="min-h-screen bg-background text-foreground font-sans selection:bg-primary/30">
	<!-- Navigation -->
	<nav class="fixed top-0 w-full z-50 px-6 py-6 flex justify-between items-center glass-dark border-b border-white/5">
		<div class="flex items-center gap-2">
			<div class="w-8 h-8 bg-primary rounded-sm flex items-center justify-center">
				<Fingerprint class="text-white w-5 h-5" />
			</div>
			<span class="text-xl font-bold tracking-tight font-mono">SIGNALLAYER<span class="text-primary italic">.AI</span></span>
		</div>
		<div class="hidden md:flex items-center gap-8 text-sm font-medium text-muted-foreground uppercase tracking-widest">
			<a href="#problem" class="hover:text-foreground transition-colors">Problem</a>
			<a href="#solution" class="hover:text-foreground transition-colors">Solution</a>
			<a href="#verification" class="hover:text-foreground transition-colors">Verification</a>
		</div>
		<Button variant="outline" size="sm" class="rounded-none border-white/10 hover:bg-white/5 font-mono text-[10px] tracking-[0.2em] uppercase">
			Request Access
		</Button>
	</nav>

	<!-- Hero Section -->
	<main class="relative pt-48 pb-24 overflow-hidden">
		<!-- Background Glows -->
		<div class="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-6xl h-full pointer-events-none">
			<div class="absolute top-[10%] left-[20%] w-[500px] h-[500px] bg-primary/10 blur-[120px] rounded-full opacity-50"></div>
			<div class="absolute top-[20%] right-[10%] w-[400px] h-[400px] bg-blue-500/5 blur-[100px] rounded-full opacity-30"></div>
		</div>

		<div class="container mx-auto px-6 relative z-10 flex flex-col items-center text-center">
			<div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-primary/20 bg-primary/5 mb-8 animate-in fade-in slide-in-from-bottom-4 duration-1000">
				<Terminal class="w-3 h-3 text-primary" />
				<span class="text-[10px] font-mono tracking-[0.3em] uppercase text-primary">Alpha 0.1: AI Verification Layer</span>
			</div>
			
			<h1 class="text-6xl md:text-8xl lg:text-9xl font-bold tracking-tighter mb-8 leading-[0.9] text-balance">
				Pierce the <br/>
				<span class="bg-gradient-to-r from-white via-white to-white/30 bg-clip-text text-transparent">Hype Supernova.</span>
			</h1>
			
			<p class="text-lg md:text-xl text-muted-foreground max-w-2xl mb-12 leading-relaxed animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-200">
				SignalLayer verifies AI signal through deep technical proof-of-work. <br class="hidden md:block"/>
				No more grifters. No more engagement bait. Just verified code.
			</p>

			<div class="flex flex-col sm:flex-row gap-4 animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-300">
				<Button size="lg" class="h-16 px-10 text-lg font-semibold rounded-none bg-primary hover:bg-primary/90 text-white shadow-[0_0_20px_rgba(0,122,255,0.3)] group">
					Join the Waitlist
					<ArrowRight class="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
				</Button>
				<Button variant="outline" size="lg" class="h-16 px-10 text-lg font-semibold rounded-none border-white/10 hover:bg-white/5">
					Explore Protocol
				</Button>
			</div>
		</div>
	</main>

	<!-- Problem Section -->
	<section id="problem" class="py-24 border-y border-white/5 relative bg-black/20">
		<div class="container mx-auto px-6 grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
			<div>
				<h2 class="text-3xl md:text-5xl font-bold tracking-tight mb-6 font-mono uppercase">The Metadata <br/>is Poisoned</h2>
				<p class="text-muted-foreground text-lg mb-8 leading-relaxed">
					Marketing-first noise is drowning out engineering-first insight. Real researchers are getting buried by high-production engagement bait. We've lost the ability to distinguish between who's shipping and who's just prompting.
				</p>
				<div class="space-y-4">
					<div class="flex items-start gap-4 p-4 glass-dark">
						<div class="mt-1 w-5 h-5 rounded-full border border-red-500/50 flex items-center justify-center text-[10px] text-red-500 font-bold">!</div>
						<div>
							<h4 class="font-bold text-sm uppercase tracking-wider mb-1">Engagement-Bait Saturation</h4>
							<p class="text-xs text-muted-foreground italic">98% of AI social output is non-technical marketing.</p>
						</div>
					</div>
					<div class="flex items-start gap-4 p-4 glass-dark">
						<div class="mt-1 w-5 h-5 rounded-full border border-red-500/50 flex items-center justify-center text-[10px] text-red-500 font-bold">!</div>
						<div>
							<h4 class="font-bold text-sm uppercase tracking-wider mb-1">Technical Obsolescence</h4>
							<p class="text-xs text-muted-foreground italic">Real signals are lost in the hype cycle speed-run.</p>
						</div>
					</div>
				</div>
			</div>
			<div class="relative aspect-square glass-dark border border-white/10 p-8 flex flex-col justify-center overflow-hidden">
				<div class="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent"></div>
				<div class="relative z-10 space-y-6">
					<div class="p-6 border border-white/5 bg-white/5 font-mono text-xs text-muted-foreground">
						<p class="text-primary mb-2">// DETECTING NOISE_LEVEL...</p>
						<div class="flex justify-between items-end gap-1 h-24">
							{#each Array(20) as _, i}
								<div class="w-2 bg-red-500/20" style="height: {Math.random() * 100}%"></div>
							{/each}
						</div>
						<p class="mt-4 text-red-500 font-bold">CRITICAL: SIGNAL_LOSS > 90%</p>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- Solution Section -->
	<section id="verification" class="py-24 relative">
		<div class="container mx-auto px-6 text-center mb-16">
			<h2 class="text-4xl md:text-6xl font-bold tracking-tighter mb-4">Verification, <span class="italic text-primary">not Discovery.</span></h2>
			<p class="text-muted-foreground max-w-xl mx-auto">
				We don't find content. We verify the human behind it. SignalLayer analyzes technical artifacts to separate practitioners from performers.
			</p>
		</div>

		<div class="container mx-auto px-6 grid grid-cols-1 md:grid-cols-3 gap-8">
			<div class="p-8 glass-dark border-t-2 border-primary/40 relative group">
				<Code2 class="w-8 h-8 text-primary mb-6 group-hover:scale-110 transition-transform" />
				<h3 class="text-xl font-bold mb-4 font-mono uppercase">Artifact Analysis</h3>
				<p class="text-sm text-muted-foreground leading-relaxed">
					Deep scanning of repository contributions, commit complexity, and architectural depth. We look for proof-of-work in the primitives.
				</p>
			</div>
			<div class="p-8 glass-dark border-t-2 border-white/10 relative group">
				<Database class="w-8 h-8 text-white/40 mb-6 group-hover:scale-110 transition-transform" />
				<h3 class="text-xl font-bold mb-4 font-mono uppercase">Signal Persistence</h3>
				<p class="text-sm text-muted-foreground leading-relaxed">
					Verification across time. We value technical longevity over post-Nov 2022 pivot velocity.
				</p>
			</div>
			<div class="p-8 glass-dark border-t-2 border-white/10 relative group">
				<Zap class="w-8 h-8 text-white/40 mb-6 group-hover:scale-110 transition-transform" />
				<h3 class="text-xl font-bold mb-4 font-mono uppercase">The Expert Grade</h3>
				<p class="text-sm text-muted-foreground leading-relaxed">
					Instant, verifiable technical ratings (S-Tier to F) that can be linked to any digital identity.
				</p>
			</div>
		</div>
	</section>

	<!-- Footer -->
	<footer class="py-24 border-t border-white/5">
		<div class="container mx-auto px-6 flex flex-col items-center text-center">
			<div class="w-12 h-12 bg-white/5 font-mono text-primary flex items-center justify-center rounded-sm mb-8">S</div>
			<h3 class="text-2xl font-bold mb-8 font-mono">SIGNALLAYER<span class="text-primary italic">.AI</span></h3>
			<p class="text-muted-foreground text-sm max-w-md mb-12">
				Building the verification layer for the agentic era. <br/>
				Designed for those who build.
			</p>
			<div class="flex gap-8 text-[10px] font-mono tracking-widest text-white/20 uppercase">
				<span>© 2024 SignalLayer Protocol</span>
				<a href="/" class="hover:text-primary transition-colors">Twitter</a>
				<a href="/" class="hover:text-primary transition-colors">GitHub</a>
			</div>
		</div>
	</footer>
</div>

<style>
	:global(html) {
		scroll-behavior: smooth;
	}
	
	/* Typography Overrides */
	:global(h1, h2, h3, h4) {
		font-family: var(--font-mono);
	}
</style>


