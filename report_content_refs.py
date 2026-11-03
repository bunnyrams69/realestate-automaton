import docx
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

def build_references(doc):
    p_ref = doc.add_paragraph()
    p_ref.paragraph_format.page_break_before = True
    p_ref.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ref.paragraph_format.line_spacing = 1.2
    p_ref.paragraph_format.space_before = Pt(14)
    p_ref.paragraph_format.space_after = Pt(12)
    p_ref.paragraph_format.keep_with_next = True
    
    r_h = p_ref.add_run("REFERENCES")
    r_h.font.name = 'Arial'
    r_h.font.size = Pt(14.0)
    r_h.font.bold = True
    r_h.font.color.rgb = RGBColor(0, 0, 0)

    references_list = [
        "1. Agnihotri, R., Dingus, R., Hu, M.Y., Krush, M.T.: Social media analytics in business-to-business sales: Lead qualification and pipeline velocity. Industrial Marketing Management 53, 172–180 (2016)",
        "2. Brown, T.B., Mann, B., Ryder, N., Subbiah, M., Kaplan, J., Dhariwal, P., Neelakantan, A., Shyam, P., Sastry, G., Askell, A.: Language models are few-shot learners. Advances in Neural Information Processing Systems (NeurIPS) 33, 1877–1901 (2020)",
        "3. Chen, H., Hailey, D.E., Wang, N., Anderson, D.: Automated intent recognition and conversational agents in e-commerce customer support. IEEE Transactions on Knowledge and Data Engineering 32(8), 1542–1555 (2020)",
        "4. Cui, L., Huang, S., Wei, F., Tan, C., Chao, C., Zhou, M.: TextBrewer: An open-source knowledge distillation toolkit for natural language processing. In: Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics (ACL), pp. 9–16. ACM, Stroudsburg (2020)",
        "5. Davenport, T., Guha, A., Grewal, D., Bressgott, T.: How artificial intelligence will change the future of marketing. Journal of the Academy of Marketing Science 48(1), 24–42 (2020)",
        "6. Følstad, A., Brandtzæg, P.B.: Chatbots and the new world of HCI. Interactions 24(4), 38–42 (2017)",
        "7. Gnewuch, U., Morana, S., Maedche, A.: Towards designing cooperative and social conversational agents for customer service. In: International Conference on Information Systems (ICIS), pp. 1–17. AIS Electronic Library, San Francisco (2017)",
        "8. Järveläinen, J.: Online purchase intentions: An empirical testing of a multiple-channel model. Journal of Research in Interactive Marketing 1(2), 102–117 (2007)",
        "9. Jurafsky, D., Martin, J.H.: Speech and Language Processing: An Introduction to Natural Language Processing, Computational Linguistics, and Speech Recognition. 3rd edn. Prentice Hall, Upper Saddle River (2023)",
        "10. Kumar, V., Rajan, B., Venkatesan, R., Lecinski, J.: Understanding the role of artificial intelligence in personalized engagement, marketing, and retailing. Journal of Retailing 95(2), 135–153 (2019)",
        "11. Liao, C.H., To, P.L., Shih, M.L.: Examining the role of modern instant messaging in enterprise customer communication. Information Systems Frontiers 19(4), 843–856 (2017)",
        "12. Liu, Y., Ott, M., Goyal, N., Du, J., Joshi, M., Chen, D., Levy, O., Lewis, M., Zettlemoyer, L., Stoyanov, V.: RoBERTa: A robustly optimized BERT pretraining approach. arXiv preprint arXiv:1907.11692 (2019)",
        "13. Overgoor, G., Chica, M., Rand, W., Weishampel, A.: Letting the computers take over: Using AI to solve marketing problems. California Management Review 61(4), 156–185 (2019)",
        "14. Syam, N., Sharma, A.: Waiting for a sales Renaissance in the fourth industrial revolution: Machine learning and artificial intelligence in sales management and personal selling. Industrial Marketing Management 69, 135–146 (2018)",
        "15. Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A.N., Kaiser, L., Polosukhin, I.: Attention is all you need. In: Advances in Neural Information Processing Systems (NeurIPS) 30, pp. 5998–6008. Curran Associates, Long Beach (2017)",
        "16. Zhang, S., Dinan, E., Urbanek, J., Szlam, A., Kiela, D., Weston, J.: Personalizing dialogue agents: I have a dog, do you have pets too? In: Proceedings of the 56th Annual Meeting of the Association for Computational Linguistics (ACL), pp. 2204–2213. Association for Computational Linguistics, Melbourne (2018)"
    ]

    for ref in references_list:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.05
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3.5)
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.first_line_indent = Inches(-0.25)
        
        r = p.add_run(ref)
        r.font.name = 'Arial'
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(0, 0, 0)

    print("References built successfully!")
