const roadmap = [
  "시즌별 선수 기록 조회",
  "경기별 팀 기록 조회",
  "일일 스크래핑 및 데이터 갱신",
  "향후 순위 예측 확장",
];

function App() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-50">
      <section className="mx-auto flex min-h-screen max-w-5xl flex-col justify-center px-6 py-16">
        <span className="inline-flex w-fit rounded-full border border-cyan-400/40 bg-cyan-400/10 px-3 py-1 text-sm text-cyan-200">
          KBO 데이터 플랫폼
        </span>
        <h1 className="mt-6 max-w-3xl text-4xl font-semibold tracking-tight sm:text-6xl">
          시즌과 경기 흐름을 따라가는 KBO 기록 서비스의 시작점
        </h1>
        <p className="mt-6 max-w-2xl text-base leading-7 text-slate-300 sm:text-lg">
          매일 갱신되는 선수 기록과 팀 기록을 한곳에서 탐색하고, 이후에는 예측 모델까지 확장할 수 있도록 프론트엔드와 백엔드를 분리한 monorepo 구조로 시작합니다.
        </p>

        <div className="mt-10 grid gap-4 sm:grid-cols-2">
          {roadmap.map((item) => (
            <article
              key={item}
              className="rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur"
            >
              <h2 className="text-lg font-medium text-white">{item}</h2>
              <p className="mt-2 text-sm leading-6 text-slate-300">
                초기 스캐폴드 단계에서 이 흐름을 확장 가능한 구조로 담아두고, 다음 단계에서 도메인 모델과 화면 기획을 구체화합니다.
              </p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}

export default App;
