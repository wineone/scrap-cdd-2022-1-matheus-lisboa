import scrapy


class QuotesSpider(scrapy.Spider):
    name = "extract_infos_deputadas"

    def start_requests(self):

        with open("lista_deputadas.txt") as file_links:
            links = file_links.readlines()

        for url in links:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        nome = response.xpath('//h2[@id="nomedeputado"]/text()').get()
        genero = "F"

        table_presenca = response.xpath('//dd[@class="list-table__definition-description"]/text()').getall()
        table_presenca_plenario  = [self.clean_text(p) for p in table_presenca]

        presenca_plenario = table_presenca_plenario[0]
        ausencia_justificada_plenario = table_presenca_plenario[1]
        ausencia_plenario = table_presenca_plenario[2]

        presenca_comissao = table_presenca_plenario[3]
        ausencia_justificada_comissao = table_presenca_plenario[4]
        ausencia_comissao = table_presenca_plenario[5]

        data_nascimento = self.clean_text(response.xpath('//ul[@class="informacoes-deputado"]//li/text()').getall()[4])

        gasto_total_par = response.xpath('//ul[@class="gastos-anuais-deputado-container"]//tbody//tr//td/text()').getall()
        gasto_total_par = [self.clean_text(g) for g in gasto_total_par]
        
        grouped_total_par = []
        for i in range(len(gasto_total_par) // 3):
            grouped_total_par.append(gasto_total_par[i*3:(i+1)*3])

        total_gasto_parlamentar = grouped_total_par[0][1]

        index_parlamen = -1
        for index,g in enumerate(grouped_total_par[1:]):
            if g[0] == 'Total Gasto':
                total_gasto_gabinete = g[1]
                index_parlamen = index

        MESES = ['JAV','FEV','MAR','MAI','ABR','JUN','JUL','AGO','SET','OUT','NOV','DEZ']
        colunas_parlamentar = [ 'gasto_jan_par', 'gasto_fev_par', 'gasto_mar_par', 'gasto_abr_par' , 'gasto_maio_par',
                    'gasto_junho_par', 'gasto_jul_par', 'gasto_agosto_par', 'gasto_set_par',
                    'gasto_out_par', 'gasto_nov_par', 'gasto_dez_par' ]
        colunas_gabinete = [
            'gasto_jan_gab', 'gasto_fev_gab', 'gasto_mar_gab', 'gasto_abr_gab' ,
            'gasto_maio_gab', 'gasto_junho_gab', 'gasto_jul_gab', 'gasto_agosto_gab',
            'gasto_set_gab', 'gasto_out_gab', 'gasto_nov_gab', 'gasto_dez_gab'
        ]
        mape_gastos_parlamentar = {v1:v2 for v1,v2 in zip(MESES, colunas_parlamentar)}
        mape_gastos_gabinete = {v1:v2 for v1,v2 in zip(MESES, colunas_gabinete)}

        total_gasto_parlamentar_prim = {v[0]:v[1] for v in grouped_total_par[:index_parlamen]}
        total_gasto_parlamentar_seg = {v[0]:v[1] for v in grouped_total_par[index_parlamen:]}
        
        gastos_parlamentar = {}
        for key,value in mape_gastos_parlamentar.items():
            if key in total_gasto_parlamentar_prim:
                gastos_parlamentar[value] = total_gasto_parlamentar_prim[key]
            else:
                gastos_parlamentar[value] = '-'

        gastos_gabinete = {}
        for key,value in mape_gastos_gabinete.items():
            if key in total_gasto_parlamentar_seg:
                gastos_gabinete[value] = total_gasto_parlamentar_seg[key]
            else:
                gastos_gabinete[value] = '-'

        salario_bruto = self.clean_text(response.xpath('//*[@id="recursos-section"]/ul/li[2]/div/a/text()').get())
        
        dic_retorno = {
            'nome':nome,
            'genero':genero,
            'presenca_plenario':presenca_plenario,
            'ausencia_justificada_plenario':ausencia_justificada_plenario,
            'ausencia_plenario':ausencia_plenario,
            'presenca_comissao':presenca_comissao,
            'ausencia_justificada_comissao':ausencia_justificada_comissao,
            'ausencia_comissao':ausencia_comissao,
            'data_nascimento':data_nascimento,
            'total_gasto_parlamentar':total_gasto_parlamentar,
            'total_gasto_gabinete':total_gasto_gabinete,
            'salario_bruto':salario_bruto
        }

        dic_retorno.update(gastos_parlamentar)
        dic_retorno.update(gastos_gabinete)

        yield dic_retorno

    def clean_text(self,t):
        t = t.replace('R$','')
        t = t.strip()
        t = t.replace('\n','')
        return t
       