import os

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Image,
    Table,
    TableStyle
)

from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)

from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors



def add_page_number(canvas, doc):

    canvas.saveState()

    canvas.setFont(
        "Helvetica",
        9
    )

    canvas.drawRightString(
        550,
        30,
        f"Page {doc.page}"
    )

    canvas.restoreState()



def generate_documentation_pdf(
    documentation: str,
    repository_id: str
):

    os.makedirs(
        "generated",
        exist_ok=True
    )


    filename = (
        f"generated/{repository_id}.pdf"
    )


    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=60,
        leftMargin=60,
        topMargin=60,
        bottomMargin=60
    )


    styles = getSampleStyleSheet()



    title_style = ParagraphStyle(
        "TitleCustom",
        parent=styles["Title"],
        fontSize=24,
        alignment=TA_CENTER,
        textColor=colors.HexColor(
            "#2563EB"
        ),
        spaceAfter=30
    )


    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["BodyText"],
        alignment=TA_CENTER,
        fontSize=12,
        textColor=colors.grey
    )


    heading_style = ParagraphStyle(
        "HeadingCustom",
        parent=styles["Heading2"],
        fontSize=16,
        textColor=colors.HexColor(
            "#2563EB"
        ),
        spaceBefore=18,
        spaceAfter=10
    )


    subheading_style = ParagraphStyle(
        "SubHeading",
        parent=styles["Heading3"],
        fontSize=13,
        textColor=colors.HexColor(
            "#0F766E"
        ),
        spaceBefore=12
    )


    body_style = ParagraphStyle(
        "BodyCustom",
        parent=styles["BodyText"],
        fontSize=11,
        leading=16,
        spaceAfter=8
    )


    bullet_style = ParagraphStyle(
        "Bullet",
        parent=body_style,
        leftIndent=20
    )



    story = []



    # -------------------------
    # COVER PAGE
    # -------------------------


    story.append(
        Spacer(1,80)
    )


    story.append(
        Paragraph(
            "AI Repository Architect",
            title_style
        )
    )


    story.append(
        Paragraph(
            "Automated Repository Documentation Report",
            subtitle_style
        )
    )


    story.append(
        Spacer(1,40)
    )


    story.append(
        Paragraph(
            f"Repository ID: {repository_id}",
            subtitle_style
        )
    )


    story.append(
        Spacer(1,20)
    )


    story.append(
        Paragraph(
            "Generated using AI-powered code analysis",
            subtitle_style
        )
    )


    story.append(
        PageBreak()
    )



    # -------------------------
    # OPTIONAL GRAPHS
    # -------------------------


    architecture_image = (
        "generated/architecture.png"
    )

    language_chart = (
        "generated/languages.png"
    )


    if os.path.exists(language_chart):

        story.append(
            Paragraph(
                "Repository Statistics",
                heading_style
            )
        )


        story.append(
            Image(
                language_chart,
                width=350,
                height=250
            )
        )


        story.append(
            Spacer(1,20)
        )



    if os.path.exists(architecture_image):

        story.append(
            Paragraph(
                "Architecture Overview",
                heading_style
            )
        )


        story.append(
            Image(
                architecture_image,
                width=400,
                height=300
            )
        )


        story.append(
            PageBreak()
        )



    # -------------------------
    # DOCUMENTATION CONTENT
    # -------------------------


    lines = documentation.split("\n")


    for line in lines:


        line = line.strip()


        if not line:

            story.append(
                Spacer(1,10)
            )

            continue



        # Main heading

        if line.startswith("# "):

            story.append(
                Paragraph(
                    line[2:],
                    heading_style
                )
            )



        # Sub heading

        elif line.startswith("## "):

            story.append(
                Paragraph(
                    line[3:],
                    subheading_style
                )
            )



        # Bullet points

        elif line.startswith("- "):

            story.append(
                Paragraph(
                    "• " + line[2:],
                    bullet_style
                )
            )



        # Simple table support

        elif "|" in line:

            columns = [
                x.strip()
                for x in line.split("|")
                if x.strip()
            ]

            if len(columns) > 1:

                table = Table(
                    [columns]
                )

                table.setStyle(
                    TableStyle(
                        [
                            (
                                "BACKGROUND",
                                (0,0),
                                (-1,-1),
                                colors.HexColor(
                                    "#DBEAFE"
                                )
                            ),
                            (
                                "GRID",
                                (0,0),
                                (-1,-1),
                                0.5,
                                colors.grey
                            )
                        ]
                    )
                )

                story.append(
                    table
                )

                story.append(
                    Spacer(1,10)
                )



        else:

            story.append(
                Paragraph(
                    line,
                    body_style
                )
            )



    doc.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )


    return filename