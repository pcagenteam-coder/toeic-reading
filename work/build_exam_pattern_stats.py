#!/usr/bin/env python3
"""Generate data/strategies/exam_pattern_stats.json from a hand-curated record list.
Every record = one number as stated by one source. Composite estimates are separate (record_type=composite).
Collected 2026-10-20 (Asia/Shanghai)."""
import json, os

OUT = "/workspace/projects/58061e9e-e075-4f3f-880c-32a61b21a72c/data/strategies/exam_pattern_stats.json"

U = {
 "iibc_format": "https://www.iibc-global.org/english/toeic/test/lr/about/format.html",
 "ets_handbook": "https://www.ets.org/pdfs/toeic/toeic-listening-reading-test-examinee-handbook.pdf",
 "ets_rm1705": "https://www.ets.org/Media/Research/pdf/RM-17-05.pdf",
 "toeicstory_102": "https://www.toeicstory.co.kr/102",
 "toeicstory_999": "https://www.toeicstory.co.kr/999",
 "toeicstory_464": "https://www.toeicstory.co.kr/464",
 "toeicstory_248": "https://www.toeicstory.co.kr/248",
 "toeicstory_2577": "https://www.toeicstory.co.kr/2577",
 "cengage_intro": "https://ngl.cengage.com/assets/downloads/toeic4e9781337396530/toeic4e-intro.pdf",
 "xdf_2018": "http://toeic.xdf.cn/201803/10761795.html",
 "toyokeizai_2016": "https://toyokeizai.net/articles/-/109179?page=4",
 "get_toeic": "https://get-toeic.com/toeic%e9%81%8e%e5%8e%bb%e5%95%8f%e9%a1%8c%e9%9b%86%e3%81%ae%e3%83%91%e3%83%bc%e3%83%885%e3%81%ae%e5%82%be%e5%90%91%e3%81%a8%e5%88%86%e6%9e%90/",
 "tranky": "https://trankyblog.com/toeic_part5",
 "eigo_koryaku": "https://eigo-koryaku.com/?p=528",
 "youlinguista": "https://youlinguista.com/toeic-part5-tips/",
 "busan_thesis": "https://www.dbpia.co.kr/journal/detail?nodeId=T16857240",
 "englishtalk": "https://www.englishtalk.jp/025-toeic-part5-overview-parts-of-speech/",
 "taisaku_lab": "https://toeic-taisaku-lab.com/toeic-part5-grammar-strategy/",
 "prep_zh": "https://prepedu.com/zh-hant/blog/toeic-reading-part-5",
 "ivy_tw": "https://www.ivy.com.tw/column/cont/2025110517562325969",
 "prep990": "https://990prep.com/en/guides/toeic-part-5-strategies",
 "scordia_p5": "https://scordia.net/blog/toeic-part5-grammar-distribution",
 "herald_2014": "https://biz.heraldcorp.com/article/145160",
 "kirihara_p6": "https://academy.kirihara.co.jp/blog/toeic/toeic-part6/",
 "fumi_p6": "https://fumi-eigo.com/toeic-part6/",
 "mikan_p6": "https://mikan.com/eigo-note/toeic-part6-guide",
 "kumata_p6": "https://kumata-eigo.create-more.net/toeic_part6/",
 "ej_p6": "https://ej.alc.co.jp/tag/TOEIC/toeic-auth-part6-20250622",
 "scordia_p6": "https://scordia.net/blog/toeic-part6-question-types",
 "mikan_p7": "https://mikan.com/eigo-note/toeic-part7-guide",
 "junpei_p7": "https://junpei-english.com/toeic-part7/",
 "studying_p7": "https://studying.jp/toeic/about-more/part7-2.html",
 "gotop_tw": "https://dlcenter.gotop.com.tw/PDFSample/ARE001800.pdf",
 "hackers_blog_p7": "https://m.blog.naver.com/hackersingang/223524784905",
 "hackers_review_2501": "https://www.hackers.co.kr/?c=s_toeic%2Ftoeic_board%2FB_TOEIC_QA&keywd=mheng_boardbanner_afterjumsu_241215&logger_kw=mheng_boardbanner_afterjumsu_241215&uid=1235120",
 "scordia_p7": "https://scordia.net/blog/toeic-part7-question-types",
 "muu_note": "https://note.com/muu_toeic/n/n765255e9672b?hl=en",
}

R = []
def add(part, category, subtype, val, year, src, note="", conf="medium", rtype="source"):
    R.append({"record_type": rtype, "part": part, "category": category, "subtype": subtype,
              "share_or_count": val, "year": year, "source_url": U.get(src, src),
              "note": note, "confidence": conf})

# ---------------- FORMAT (official) ----------------
add("ALL","format","Part5 questions","30",2025,"iibc_format","IIBC official format page","high")
add("ALL","format","Part6 questions","16 (4 texts x 4; answers are word, phrase or sentence)",2025,"iibc_format","IIBC official","high")
add("ALL","format","Part7 single-passage questions","29",2025,"iibc_format","IIBC official; also states sentence-insertion questions exist","high")
add("ALL","format","Part7 multiple-passage questions","25",2025,"iibc_format","IIBC official","high")
add("ALL","format","Part7 single passages","10 texts, 2-4 questions each",2025,"ets_handbook","ETS Examinee Handbook (paper)","high")
add("ALL","format","Part7 multiple passages","5 sets (double or triple) x 5 questions",2025,"ets_handbook","ETS Examinee Handbook","high")
add("ALL","format","Part7 double/triple split","double 2 sets=10q; triple 3 sets=15q",2016,"toyokeizai_2016","also toeicstory_102 (2015) and mikan_p7","high")
# 2016 change
add("ALL","2016_change","Part5 count","40 -> 30",2017,"ets_rm1705","ETS research memo, pre-update vs updated","high")
add("ALL","2016_change","Part6 count","12 -> 16 (+1 sentence-choice item per text)",2017,"ets_rm1705","ETS RM-17-05; sentence item per text: cengage_intro, toeicstory_248","high")
add("ALL","2016_change","Part7 count","48 -> 54",2017,"ets_rm1705","ETS RM-17-05","high")
add("ALL","2016_change","Part7 single passages","9 passages (2-5q, 28q) -> 10 passages (2-4q, 29q)",2015,"toeicstory_102","YBM Korea TOEIC Committee blog","high")
add("ALL","2016_change","Part7 multiple passages","4 double sets (20q) -> 2 double + 3 triple sets (25q)",2015,"toeicstory_102","","high")
add("ALL","2016_change","Part7 new item types","text-message/online chat (multi-writer), writer-intent items, sentence-insertion, triple passages",2016,"cengage_intro","Cengage TOEIC 4e intro; same list in xdf_2018","high")
add("ALL","2016_change","rollout dates","Japan/Korea 2016-05-29; other public tests from 2018-04",2018,"xdf_2018","新东方 relays ETS 2018-01 release","high")
add("ALL","difficulty","p-value by part (updated pilot forms E/F)","P5 .67/.68; P6 .55/.57; P7 .48/.55 (P7 single .53/.62, multi .42/.45)",2017,"ets_rm1705","proportion correct; useful as difficulty prior, not frequency","high")

# ---------------- PART 5 ----------------
P5="Part5"
# get-toeic (Korean ETS 기출 Vol.3 analysis relayed; 7 real Korean tests + 3)
gt=[("grammar","tense","6% (~1.8/30)"),("grammar","pronoun","6% (~1.8/30)"),("grammar","determiner (those/each/whose...)","3% (~0.9/30)"),
    ("grammar","participle","4% (~1.2/30)"),("grammar","other grammar","6% (~1.8/30)"),
    ("word_form","noun slot","10% (3/30)"),("word_form","adjective slot","4% (1.2/30)"),("word_form","adverb slot","8% (2.4/30)"),
    ("vocabulary","verb","8%"),("vocabulary","adjective","8%"),("vocabulary","noun","8%"),("vocabulary","adverb","9%"),
    ("vocabulary","preposition (meaning)","10% (3/30)"),("vocabulary","conjunction (meaning)","5%"),("vocabulary","phrase/idiom","5%")]
for c,s,v in gt:
    add(P5,c,s,v,2021,"get_toeic","Analysis printed in ETS TOEIC 既出問題集3 (Korean real tests, pub. 2021-12), relayed by get-toeic; prep/conj counted as VOCAB here","medium-high")
add(P5,"grammar","TOTAL","25%",2021,"get_toeic","","medium-high")
add(P5,"word_form","TOTAL","22%",2021,"get_toeic","","medium-high")
add(P5,"vocabulary","TOTAL (incl. prep/conj/phrase)","53%",2021,"get_toeic","","medium-high")
# trankyblog: official prep book 7-9, 6 tests 180 q
for s,v in [("vocabulary","30.0% (54/180)"),("word_form","25.6% (46/180)"),("preposition","10.6% (19/180)"),("conjunction","9.4% (17/180)"),
            ("adverb (choice)","8.3% (15/180)"),("verb form (tense/voice)","7.7% (14/180)"),("pronoun","7.2% (13/180)"),("comparative","1.1% (2/180)")]:
    add(P5,"type",s,v,2023,"tranky","公式TOEIC L&R 問題集7-9, 6 tests; blogger's own classification","medium")
# eigo-koryaku
for s,v in [("vocabulary","40.0% (12/30)"),("word_form","16.7% (5)"),("preposition","13.3% (4)"),("verb","10.0% (3)"),
            ("pronoun","6.7% (2)"),("comparative","6.7% (2)"),("adverb","3.3% (1)"),("conjunction","3.3% (1)")]:
    add(P5,"type",s,v,2016,"eigo_koryaku","one official problem-book test (30 q); tiny sample; tense/article 0","low")
add(P5,"type","grammar vs vocabulary","grammar >60%, vocabulary <40%",2022,"youlinguista","公式問題集7, 2 tests (60 q); exact figures only in chart image","medium")
# YBM toeicstory 999 (2018)
for c,s,v in [("grammar","tense","~2 per test"),("grammar","pronoun","~2 per test"),("grammar","determiner","~1 per test"),("grammar","participle","~1 per test"),
              ("vocabulary","verb / noun / adjective / adverb","2-3 each per test"),("vocabulary","preposition","~3 per test"),
              ("vocabulary","conjunction / phrase","0 in some tests"),("word_form","noun","2-3 per test")]:
    add(P5,c,s,v,2018,"toeicstory_999","YBM 한국TOEIC위원회, from 'ETS 토익 정기시험 기출문제집' trend analysis","medium-high")
add(P5,"type","grammar vs vocabulary","grammar ~20 / vocabulary ~10 (of 30)",2016,"toeicstory_464","expert quote, first months after 2016 update","medium")
add(P5,"type","grammar vs vocabulary","grammar 767/870 (88.2%), vocabulary 103/870 (11.8%)",2023,"busan_thesis",
    "Busan Nat'l Univ MA thesis; 29 YBM 기출 tests post-2016; VOCAB defined strictly as all 4 options same POS -> much lower vocab share than other sources",
    "medium (definition differs)")
add(P5,"grammar_rank","frequency order of grammar categories","noun > adjective > adverb > preposition > clause/conjunction > determiner/pronoun > tense > passive > to-infinitive > modal",2023,"busan_thesis","rank only; counts behind paywall","medium")
add(P5,"type","vocab / word_form / other grammar","9-10 (30%) / 7-8 (25%) / 13-14 (45%)",2025,"englishtalk","claims IIBC reference but IIBC does not publish breakdown","low")
add(P5,"type","word_form / vocab / pronoun+relative / paired expressions","~30% / ~25% / ~10% / ~10%",2026,"taisaku_lab","no sample stated","low")
add(P5,"type","grammar vs vocabulary","grammar 60-70%, vocabulary 30-40%; word_form 25-30%",2025,"prep_zh","claims 'ETS official stats' (unverified; ETS publishes none)","low")
add(P5,"type","grammar vs vocabulary","grammar ~1/3, vocabulary ~2/3",2025,"ivy_tw","Taiwan teacher column (常春藤); counts prep/conj choices as vocab","low")
add(P5,"type","vocab / word_form / grammar / connectors","~25% / ~30% / ~35% / ~10%",2025,"prep990","no sample stated","low")
for s,v in [("preposition","12.5% of 546 grammar items"),("conjunction","10.1%"),("word-form","10.1%"),("relative pronoun","8.2%"),
            ("verb pattern","7.3%"),("verb form","7.1%"),("gerund","6.2%"),("passive","6.2%"),("tense","6.2%"),("subject-verb agreement","5.9%"),
            ("conditional","5.3%"),("inversion","5.3%")]:
    add(P5,"grammar_sub (practice bank)",s,v,2026,"scordia_p5","NOT exam data: site's own AI-generated practice bank, multi-tag; do not use as weight","very low")
add(P5,"trend","grammar-only items","<=10 per test (was 10-12); more meaning-dependent items, e.g. two noun options after 'the'",2014,"herald_2014","pre-2016 Korean trend article","medium")
add(P5,"trend","vocabulary style","more confusable similar-form words (diagnostic vs diagnosable), polysemy, wider paraphrase",2026,"toeicstory_2577","YBM 2026 trend article (qualitative)","medium")

# ---------------- PART 6 ----------------
P6="Part6"
add(P6,"sentence_insertion","sentence choice","4 per test (1 per text) = 25%",2025,"iibc_format","fixed by format; confirmed cengage_intro, toeicstory_248, mikan_p6","high")
for s,v in [("vocabulary","~6"),("sentence choice","~4"),("grammar (Part5-type)","~3"),("tense (context)","~2"),("connective / conjunctive adverb","~1")]:
    add(P6,"type",s,v+" of 16",2022,"kirihara_p6","桐原 KIRIHARA Online Academy","medium")
    add(P6,"type",s,v+" of 16",2025,"fumi_p6","identical table to KIRIHARA (likely copied)","low")
for s,v in [("vocabulary","~2 per text (~8/test)"),("word_form / grammar","~1 per text (~4/test)"),("sentence choice","1 per text (4/test)")]:
    add(P6,"type",s,v,2018,"toeicstory_999","YBM; vocab: verb/noun/adverb/phrase 1-2 each; word_form noun/adj > adverb","medium-high")
for s,v in [("context-independent grammar","~8"),("context-dependent (tense/pronoun/conj/vocab)","~4"),("sentence insertion","4")]:
    add(P6,"solve_type",s,v+" of 16",2025,"mikan_p6","mikan 英語ノート","medium")
add(P6,"type","vocabulary / sentence / grammar","vocab just under half (~7), sentence 4, rest grammar",2019,"kumata_p6","","low")
add(P6,"solve_type","independent (single-sentence solvable)","about half",2025,"ej_p6","ALC English Journal","medium")
add(P6,"passage_type","letter/email ('Dear')","48-54% of practice items",2026,"scordia_p6","NOT exam data (AI practice bank)","very low")

# ---------------- PART 7 ----------------
P7="Part7"
for s,v in [("detail / content (内容把握)","~20"),("option-matching / true (選択肢照合)","~12"),("inference (推測)","~8"),("main idea / purpose (テーマ)","~5"),
            ("synonym (語彙)","~3"),("NOT","~2"),("intent (意図)","~2"),("sentence insertion (文挿入)","~2")]:
    add(P7,"question_type",s,v+" of 54",2025,"junpei_p7","ゼロから極める英語塾; per-test approximation, sums to 54","medium")
for s,v in [("whole-text (purpose/theme)","8-10"),("detail (who/when/where/what)","20-25"),("hard items total","21-23"),
            ("inference (suggested/implied/most likely)","~15"),("NOT","0-3"),("intent","~2"),("sentence insertion","2 (single passages)")]:
    add(P7,"question_type",s,v+" of 54",2026,"mikan_p7","mikan 英語ノート (updated 2026-07)","medium")
add(P7,"question_type","intent","2 of 54",2025,"studying_p7","STUDYing","medium")
add(P7,"distribution","synonym location","mostly in double/triple passages",2018,"toeicstory_999","YBM","medium-high")
add(P7,"distribution","cross-reference (linking) items","~1 per double set, ~2 per triple set (=> ~8/test)",2018,"toeicstory_999","also hackers_blog_p7 (2024): double 1, triple ~2","medium-high")
add(P7,"distribution","cross-reference (linking) items","1-2 per double set, 2-3 per triple set",2020,"gotop_tw","碁峰 (Taiwan) TOEIC mock-test book sample PDF; year approx.","medium")
add(P7,"distribution","intent item location","1 in each 2-q or 4-q single passage that is text-message chain / online chat",2020,"gotop_tw","implies >=2 chat/text passages per test (inferred)","medium")
add(P7,"distribution","sentence-insertion location","1 in each 3-q or 4-q single passage; usually article / email-letter",2020,"gotop_tw","","medium")
add(P7,"question_type","synonym (one real test, 2025-01-26 KR)","3",2025,"hackers_review_2501","Hackers instructor live review; single-passage q-count pattern 2-2-3-2-3-3-4-4-3-4; many 'What is concluded' items","medium")
add(P7,"passage_type","email/letter + article","50-60% of passages",2018,"toeicstory_999","YBM, from 기출문제집 analysis","medium-high")
add(P7,"passage_type","genres listed","email/letter, ad, notice, article, text message, form/invoice/schedule, instructions/warranty, web page",2026,"mikan_p7","no counts","medium")
add(P7,"passage_type","ETS directions examples","magazine/newspaper articles, e-mails, instant messages",2025,"ets_handbook","","high")
for s,v in [("detail","57.3%"),("inference","16.3%"),("synonym","10.6%"),("purpose","7.8%"),("calculation","6.9%"),("NOT","5.9%"),
            ("reason","4.5%"),("intent","3.8%"),("cross-reference","3.5%"),("sentence insertion","0.8%")]:
    add(P7,"question_type (practice bank)",s,v+" of 1325 items",2026,"scordia_p7","NOT exam data (AI-generated practice bank); multi-tag","very low")
for s,v in [("email","11.6%"),("text message / chat","10.1%"),("notice/announcement","7.2%"),("policy","6.3%"),("memo","3.9%"),("article","3.5%"),
            ("review","3.2%"),("job posting","3.2%"),("advertisement","3.1%")]:
    add(P7,"passage_type (practice bank)",s,v+" of items",2026,"scordia_p7","NOT exam data; 478 items untagged","very low")
add(P7,"trend","distractors","more partial-match options and abstract correct answers",2026,"muu_note","Japanese high scorer blog (qualitative)","low")
add(P7,"trend","linked passages","longer; whole-passage reading needed; 'What is concluded' wording rising",2025,"hackers_review_2501","single test review","low")

# ---------------- COMPOSITE (our estimates) ----------------
def comp(part, cat, sub, val, srcs, note):
    R.append({"record_type":"composite","part":part,"category":cat,"subtype":sub,"share_or_count":val,"year":2026,
              "source_url":"; ".join(U[s] for s in srcs),"note":note,"confidence":"estimate"})
comp(P5,"vocabulary","same-POS meaning (content words + phrase; excl. prep/conj)","30-40% (9-12 of 30)",["tranky","eigo_koryaku","youlinguista","toeicstory_464","toeicstory_999","get_toeic"],
     "get_toeic 38% after removing prep/conj; outlier busan_thesis 11.8% (strict definition) excluded")
comp(P5,"word_form","POS slot (noun/adj/adv/verb)","20-27% (6-8)",["get_toeic","tranky","eigo_koryaku","toeicstory_999"],"noun slot most frequent (busan_thesis rank, toeicstory_999)")
comp(P5,"preposition","preposition choice incl. prep vs conj","10-13% (3-4)",["get_toeic","tranky","eigo_koryaku","toeicstory_999"],"")
comp(P5,"conjunction","subordinating/correlative/conj. adverb","3-9% (1-3)",["get_toeic","tranky","eigo_koryaku"],"prep+conj combined 13-20%")
comp(P5,"verb_form","tense/voice/agreement/participle/non-finite","8-12% (2-4)",["get_toeic","tranky","eigo_koryaku","toeicstory_999"],"")
comp(P5,"pronoun_determiner","case/reflexive/determiner/quantifier","7-10% (2-3)",["get_toeic","tranky","eigo_koryaku","toeicstory_999"],"")
comp(P5,"relative","relative pronoun/adverb","0-3% (0-1) - weak evidence",["get_toeic","tranky"],"rarely broken out; folded into 'other grammar'")
comp(P5,"comparative","comparative/superlative","1-3% (0-1)",["tranky","eigo_koryaku"],"")
comp(P6,"sentence_insertion","sentence choice","4 of 16 (25%) fixed",["iibc_format","cengage_intro"],"")
comp(P6,"vocabulary","word/phrase meaning in context","5-8 (31-50%)",["kirihara_p6","toeicstory_999","kumata_p6"],"")
comp(P6,"grammar","word_form + verb tense/form + pronoun","3-5 (tense ~2)",["kirihara_p6","toeicstory_999","mikan_p6"],"")
comp(P6,"connective","conjunctive adverb (however/therefore...)","~1 (0-2)",["kirihara_p6"],"")
comp(P7,"question_type","detail / specific info","20-25 (37-46%)",["junpei_p7","mikan_p7"],"")
comp(P7,"question_type","true/indicated (option matching)","~10-12 (overlaps inference)",["junpei_p7"],"many 'What is indicated' items are classed as inference by others")
comp(P7,"question_type","inference (suggested/implied/most likely/concluded)","8-15",["junpei_p7","mikan_p7"],"")
comp(P7,"question_type","main idea / purpose","5-10",["junpei_p7","mikan_p7"],"")
comp(P7,"question_type","synonym","2-4",["junpei_p7","hackers_review_2501"],"mostly in multi-passage sets")
comp(P7,"question_type","NOT","1-3",["junpei_p7","mikan_p7"],"")
comp(P7,"question_type","intent (quoted phrase in chat)","2",["mikan_p7","junpei_p7","studying_p7"],"")
comp(P7,"question_type","sentence insertion","2",["mikan_p7","junpei_p7","gotop_tw"],"")
comp(P7,"question_type","cross-reference (overlaps above)","6-10",["toeicstory_999","hackers_blog_p7","gotop_tw"],"")
comp(P7,"passage_type","email/letter + article","~50-60% of ~23 documents (~12-14 docs)",["toeicstory_999"],"single source; documents per test = 10 + 2x2 + 3x3 = 23")
comp(P7,"passage_type","text message / online chat",">=2 documents (inferred from 2 intent items)",["gotop_tw","mikan_p7"],"inferred")
comp(P7,"passage_type","ad / notice-memo / form-invoice-schedule / web page / review","remaining ~7-9 docs; no per-type count source found",["mikan_p7"],"gap")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT,"w",encoding="utf-8") as f:
    json.dump(R,f,ensure_ascii=False,indent=1)
print(len(R), "records;", sum(r["record_type"]=="source" for r in R), "source,", sum(r["record_type"]=="composite" for r in R), "composite")
print("distinct source urls:", len({r["source_url"] for r in R if r["record_type"]=="source"}))
